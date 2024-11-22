import sys
import os, re, shutil

# Ensure the current directory is in sys.path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from colorama import Fore, Style
from generate_pytest import generate_python_script
import subprocess
import ast
import pkg_resources
import argparse


def get_file_path(module_name, file_name):
    try:
        resource_path = pkg_resources.resource_filename(module_name, file_name)
        return resource_path
    except FileNotFoundError:
        print(f"File {file_name} not found in module {module_name}")
        return None

def get_esbmc_path():
    return os.path.join(os.path.dirname(sys.executable), 'esbmc')

def print_banner():
  print("=======================================\n                ETHCHECK\n=======================================")
  subprocess.run([get_esbmc_path(), '--version'], check=True)

def get_function_names(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def get_counterexample(std_err):
    start_marker = "[Counterexample]"
    end_marker = "VERIFICATION FAILED"
    start_index = std_err.find(start_marker)
    end_index = std_err.find(end_marker)
    return std_err[start_index:end_index].strip() if start_index != -1 and end_index != -1 else ""

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
        subprocess.run(full_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        print(Fore.GREEN + f"{func} ✓")

    except subprocess.TimeoutExpired:
        print(Fore.YELLOW + f"{func}: Timeout")

    except subprocess.CalledProcessError as e:  ## ESBMC execution failed

        # Filter ESBMC output to get counterexample
        counterexample = get_counterexample(e.stderr)

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

        except ValueError as e:
            # ESBMC couldn't create a testcase so we just present the counterexample.
            print_esbmc_output(func, full_cmd, counterexample)
        except subprocess.CalledProcessError as e:
            # Issue confirmed by test. Print ESBMC and Pytest logs.
            print_esbmc_output(func, full_cmd, counterexample)
            print(Fore.BLUE + f"Pytest command: {e.cmd}\n" + Style.RESET_ALL)
            print(e.stdout)
            if os.path.isfile("testcase.xml"):
              os.remove("testcase.xml")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--deneb', action='store_true', help='Verify deneb fork')
    parser.add_argument('--file', type=str, help='Verify a specific file')

    args = parser.parse_args()

    if args.deneb:
        python_file = get_file_path('eth2spec.deneb', 'mainnet.py')
    elif args.file:
        python_file = args.file
    else:
        python_file = 'ethcheck/spec.py'

    if not os.path.exists(python_file):
        print("File not found:", python_file)
        sys.exit(2)

    print_banner();
    print(f"Verifying file: {python_file}\n")

    #command = [get_esbmc_path(), '--incremental-bmc', '--compact-trace', '--unsigned-overflow-check', '--generate-test', python_file]
    command = [get_esbmc_path(), '--incremental-bmc', '--compact-trace', '--generate-test', python_file]
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
