# EthCheck

EthCheck is a command-line tool for testing and verifying the Ethereum [Consensus Specification](https://github.com/ethereum/consensus-specs) using the [ESBMC](https://github.com/esbmc/esbmc) model checker. EthCheck includes:
- Verification of individual functions across all available forks;
- Automatic generation of test cases for each detected issue;
- Execution of these tests against [eth2spec](https://pypi.org/project/eth2spec/) to confirm results;
- Availability as a [pip package](https://pypi.org/project/ethcheck/0.1.0/) for easy installation.

## Architecture

The figure bellow illustrates the EthCheck architecture.

![image](https://github.com/user-attachments/assets/97a4e08f-b139-4135-a44d-206c6aa84d41)

## Installation
EthCheck is currently supported on **Linux**.

### 1. Install dependencies
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git-lfs
./scripts/install_deps.sh
```
### 2. Activate the Virtual Environment
Activate the Python virtual environment created during the step above.
```
source ethcheck_env/bin/activate
```
### 3. Install EthCheck
```
pip install .
```

## Usage
**Important**: Ensure the virtual environment is active by running the command ```source ethcheck_env/bin/activate``` before using EthCheck. The terminal should display **\<ethcheck_env\>** if the environment is active.

### Verify a specific file
```
ethcheck --file ethcheck/spec.py
```

### List available forks
```
ethcheck --list-forks
```

### Verify a specific fork
```
ethcheck --fork <fork-name>
```


## ESBMC version
EthCheck ships a bundled ESBMC binary (installed into `ethcheck_env/bin/esbmc`):

Git hash: 1dffbe270c </br>
Git tag: consensus-v1 </br>
MD5: 618f1fd89c399102865f9e366d164cb6 </br>

### Compatibility and using a different ESBMC

EthCheck verifies Python files, so the ESBMC binary it runs **must be built with the
Python frontend** (`-DENABLE_PYTHON_FRONTEND=ON`). Building ESBMC from source also
requires **clang/LLVM >= 18** — otherwise the build fails with
`'clang::CXXMethodDecl' has no member named 'isExplicitObjectMemberFunction'`.
EthCheck is tested with the bundled binary and with **ESBMC 8.3.0**.

To use a different ESBMC build, either:
- pass it explicitly: `ethcheck --esbmc /path/to/esbmc ...`
- set an environment variable: `export ESBMC_PATH=/path/to/esbmc`
- or replace `ethcheck_env/bin/esbmc` with your binary.

EthCheck runs a preflight check and exits with a clear message if the selected ESBMC
lacks the Python frontend or is too old.

## Acknowledgment

We thank the [Ethereum Foundation](https://www.linkedin.com/company/ethereum-foundation/) for supporting our research team on this project.

