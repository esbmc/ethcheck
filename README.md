# EthCheck

EthCheck is a command-line tool for verifying the Ethereum [Consensus Specification](https://github.com/ethereum/consensus-specs) using the [ESBMC](https://github.com/esbmc/esbmc) model checker. EthCheck runner includes:
- Automatically generating test cases for each detected issue;
- Executing these tests against [eth2spec](https://pypi.org/project/eth2spec/) for confirmation;
- A comprehensive pip package with detailed documentation.

## Architecture

Figure 1 illustrates the EthCheck architecture.

![image](https://github.com/user-attachments/assets/15433b40-34b2-4c29-84ee-9113337c1cd2)


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

### Verify the Deneb fork specification
```
ethcheck --deneb
```

## ESBMC version
Git hash: 1dffbe270c </br>
Git tag: consensus-v1 </br>
MD5: 618f1fd89c399102865f9e366d164cb6 </br>

## Acknowledgment

We thank the [Ethereum Foundation](https://www.linkedin.com/company/ethereum-foundation/) for supporting our research team on this project.

