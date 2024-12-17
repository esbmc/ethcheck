# EthCheck

EthCheck is a command-line tool for testing and verifying the Ethereum [Consensus Specification](https://github.com/ethereum/consensus-specs) using the [ESBMC](https://github.com/esbmc/esbmc) model checker. EthCheck runner includes:
- Automatically generating test cases for each detected issue;
- Executing these tests against [eth2spec](https://pypi.org/project/eth2spec/) for confirmation;
- A comprehensive [pip package](https://pypi.org/project/ethcheck/0.1.0/) with detailed documentation.

## Architecture

The figure illustrates the EthCheck architecture.

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
Git hash: 1dffbe270c </br>
Git tag: consensus-v1 </br>
MD5: 618f1fd89c399102865f9e366d164cb6 </br>

## Acknowledgment

We thank the [Ethereum Foundation](https://www.linkedin.com/company/ethereum-foundation/) for supporting our research team on this project.

