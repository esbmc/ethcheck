# EthCheck

EthCheck is a command-line tool for testing and verifying the Ethereum [Consensus Specification](https://github.com/ethereum/consensus-specs) using the [ESBMC](https://github.com/esbmc/esbmc) model checker. EthCheck includes:
- Verification of individual functions across all available forks;
- Automatic generation of test cases for each detected issue;
- Execution of these tests against [eth2spec](https://pypi.org/project/eth2spec/) to confirm results;


## Architecture

The figure bellow illustrates the EthCheck architecture.

![image](https://github.com/user-attachments/assets/97a4e08f-b139-4135-a44d-206c6aa84d41)

## Installation
EthCheck is currently supported on **Linux**.


```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git-lfs
pip install eth2spec
pip install ethcheck
```


## Usage
**Important**: Ensure the virtual environment is active by running the command below:

```
python3 -m venv ethcheck_env
source ethcheck_env/bin/activate
```

The terminal should display **\<ethcheck_env\>** if the environment is active.

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