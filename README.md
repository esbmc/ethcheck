# EthCheck

EthCheck is a command-line tool for verifying the Ethereum [Consensus Specification](https://github.com/ethereum/consensus-specs) using the [ESBMC](https://github.com/esbmc/esbmc) model checker.

## Installation
EthCheck is currently supported on **Linux**.

### 1. Install dependencies
```bash
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
