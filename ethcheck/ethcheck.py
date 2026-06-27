import sys
import os, re, shutil

# Ensure the current directory is in sys.path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from colorama import Fore, Style
from generate_pytest import generate_python_script
from list_forks import list_forks
import subprocess
import ast
import pkg_resources
import argparse
import generate_pytest

def get_file_path(module_name):
    mainnet_file = 'mainnet.py'
    spec_file = 'spec.py'
    resource_path = pkg_resources.resource_filename(module_name, mainnet_file)
    generate_pytest.module_name = 'mainnet'
    if not os.path.exists(resource_path):
        resource_path = pkg_resources.resource_filename(module_name, spec_file)
        generate_pytest.module_name = 'spec'
    return resource_path

def get_esbmc_path(override=None):
    # Resolution order: explicit override (CLI --esbmc) > $ESBMC_PATH > bundled binary.
    return (override
            or os.environ.get('ESBMC_PATH')
            or os.path.join(os.path.dirname(sys.executable), 'esbmc'))

def preflight_check(esbmc_path):
    # Runs `esbmc --help` once and reuses the output to (a) confirm the binary
    # runs, (b) check it exposes the Python frontend and current test-case flag,
    # and (c) extract the version for the banner -- so startup spawns ESBMC just
    # once instead of also calling --version separately. Returns the version.
    hint = "Use the bundled binary, or set ESBMC_PATH / --esbmc to a compatible build."

    if not os.path.isfile(esbmc_path) or not os.access(esbmc_path, os.X_OK):
        print(f"Error: ESBMC binary not found or not executable: {esbmc_path}\n{hint}")
        sys.exit(4)

    try:
        help_text = subprocess.run([esbmc_path, '--help'], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"Error: could not run ESBMC at {esbmc_path}: {exc}\n{hint}")
        sys.exit(4)

    # EthCheck verifies .py files, so ESBMC must expose the Python frontend and
    # the current test-case flag. The --python option is emitted in --help only
    # when ESBMC is built with -DENABLE_PYTHON_FRONTEND=ON (the whole "Python
    # frontend" option group is #ifdef'd on that flag), so its presence is a
    # reliable signal -- it is listed verbatim as "--python" in such builds.
    if '--python' not in help_text or '--generate-testcase' not in help_text:
        print(f"Error: ESBMC at {esbmc_path} lacks the Python frontend or is too old.\n"
              "EthCheck needs an ESBMC built with -DENABLE_PYTHON_FRONTEND=ON "
              f"(building from source requires clang/LLVM >= 18).\n{hint}")
        sys.exit(4)

    # ESBMC prints its version in the --help banner ("... ESBMC 8.3.0 ...").
    match = re.search(r'ESBMC\s+\d[\w.]*', help_text)
    return match.group(0) if match else 'ESBMC (version unknown)'

def print_banner(esbmc_version):
  print("=======================================\n                ETHCHECK\n=======================================")
  print(esbmc_version)

def get_function_names(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def get_counterexample(output):
    start_marker = "[Counterexample]"
    end_marker = "VERIFICATION FAILED"
    start_index = output.find(start_marker)
    end_index = output.find(end_marker)
    return output[start_index:end_index].strip() if start_index != -1 and end_index != -1 else ""

def classify_esbmc_output(output):
    # Classify on ESBMC's verdict text, not the process exit code: ESBMC exits
    # non-zero both for a real counterexample and for an error (parse/type
    # error, unsupported construct, internal limitation) that never reaches a
    # verdict. The two cases must not be conflated. Check FAILED first so a
    # counterexample is never masked if both markers ever co-occur -- a bug
    # finder must fail safe toward reporting the violation.
    if "VERIFICATION FAILED" in output:
        return "failed"
    if "VERIFICATION SUCCESSFUL" in output:
        return "success"
    return "error"

def get_esbmc_error(output):
    for line in output.splitlines():
        if line.startswith("ERROR:"):
            return line.strip()
    return "ESBMC produced no verdict"

def print_esbmc_output(func, cmd, output):
    if func:
        print(Fore.RED + f"{func} ✗")
    cmd_str = ' '.join(cmd)
    print(Fore.BLUE + f"ESBMC command: {cmd_str}\n" + Style.RESET_ALL)
    if output:
      print(f"{output}\n")

def get_function_arg_types(file_path, func_name):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return [arg.annotation.id if isinstance(arg.annotation, ast.Name) else 'unknown' for arg in node.args.args]
    return []

def verify_function(func, command):
    full_cmd = command + ['--function', func]
    try:
        # Execute ESBMC in a child process
        result = subprocess.run(full_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        print(Fore.YELLOW + f"{func}: Timeout")
        return

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    status = classify_esbmc_output(output)

    if status == "success":
        print(Fore.GREEN + f"{func} ✓")
        return

    if status == "error":
        # ESBMC could not analyze the function (parse/type error, unsupported
        # construct, internal limitation) -- this is not a counterexample.
        print(Fore.YELLOW + f"{func} ⚠  ESBMC could not analyze: {get_esbmc_error(output)}")
        return

    # status == "failed": a genuine counterexample.
    counterexample = get_counterexample(output)

    if not os.path.exists("testcase.xml"):
        print_esbmc_output(func, full_cmd, counterexample)
        return

    try:
        # Generate Python file with test case.
        tc_name = f'test_consensus_{func}.py'
        # Get argument types for the function
        python_file = command[-1] # Ensure that the Python file is always the last element in the command
        arg_types = get_function_arg_types(python_file, func)

        tests_folder = "/tmp/ethcheck"
        os.makedirs(tests_folder, exist_ok=True)
        test_file = tests_folder + "/" + tc_name
        generate_python_script("testcase.xml", func, arg_types, test_file)

        # Execute test in a child process using Pytest to confirm issue.
        subprocess.run(['pytest', test_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Print verificatin sucessfull when the issue is not confirmed by Pytest
        print(Fore.GREEN + f"{func} ✓")

        # Delete passed test
        if os.path.isfile(test_file):
          os.remove(test_file)

    except ValueError:
        # ESBMC couldn't create a testcase so we just present the counterexample.
        print_esbmc_output(func, full_cmd, counterexample)
    except subprocess.CalledProcessError as e:
        # Issue confirmed by test. Print ESBMC and Pytest logs.
        print_esbmc_output(func, full_cmd, counterexample)
        print(Fore.BLUE + f"Pytest command: {e.cmd}\n" + Style.RESET_ALL)
        print(e.stdout)
        if os.path.isfile("testcase.xml"):
          os.remove("testcase.xml")
        sys.exit(3)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='Verify a specific file')
    parser.add_argument('--list-forks', action='store_true', help='List available forks')
    parser.add_argument('--fork', type=str, help='Verify a specific fork')
    parser.add_argument('--function', type=str, help='Verify a specific function')
    parser.add_argument('--esbmc', type=str, help='Path to the ESBMC binary to use (overrides $ESBMC_PATH and the bundled binary)')

    args = parser.parse_args()

    if args.list_forks:
        # Call list_forks and print the list
        forks = list_forks()
        if forks:
            print("Available forks:", ", ".join(forks))
        else:
            print("No forks found.")
        return  # Exit after listing forks

    if args.fork:
        forks = list_forks()
        if args.fork not in forks:
            print(f"Error: Fork '{args.fork}' not found.\nAvailable forks: {', '.join(forks)}")
            sys.exit(1)
        python_file = get_file_path(f'eth2spec.{args.fork}')
        generate_pytest.fork_name = args.fork
    elif args.file:
        python_file = args.file
    else:
        python_file = 'ethcheck/spec.py'

    if not os.path.exists(python_file):
        print("File not found:", python_file)
        sys.exit(2)

    python_function = None
    if args.function:
        python_function = args.function

    esbmc_path = get_esbmc_path(args.esbmc)
    esbmc_version = preflight_check(esbmc_path)

    print_banner(esbmc_version);
    print(f"Verifying file: {python_file}\n")

    #command = [esbmc_path, '--incremental-bmc', '--compact-trace', '--unsigned-overflow-check', '--generate-testcase', python_file]
    command = [esbmc_path, '--incremental-bmc', '--compact-trace', '--generate-testcase', python_file]

    # Verify a single function
    if python_function:
        verify_function(python_function, command)
    else:
    # Verify all functions
        function_list = get_function_names(python_file)
        for func in function_list:
            verify_function(func, command)

    # clean temporary files
    for d in os.listdir("/tmp"):
        if re.match(r"^esbmc-python-astgen-", d):
            shutil.rmtree(f"/tmp/{d}", ignore_errors=True)

    print()

if __name__ == "__main__":
    main()
