#!/bin/bash

CONSENSUS_RELEASE="v1.5.0-alpha.4"

# Check if git-lfs is installed
if which git-lfs &> /dev/null; then
    echo -e "git-lfs is already installed"
else
    echo -e "ERROR: You need to install the git-lfs package, for example via:"
    echo -e "sudo apt install -y git-lfs"
    exit 1
fi

if which python3 &> /dev/null; then
    echo -e "python is already installed"
else
    echo -e "ERROR: You need to install python3 package, for example via:"
    echo -e "sudo apt install -y python3-venv python3-pip"
    exit 1
fi

if which pip3 &> /dev/null; then
    echo -e "pip3 is already installed"
else
    echo -e "ERROR: You need to install python3 package, for example via:"
    echo -e "sudo apt install -y python3-pip"
    exit 1
fi

venv_installed=$(python -m venv --help | grep usage)
if [[ -n "$venv_installed" ]]; then
    echo "Python venv package is installed."
else
    echo "Python venv package is not installed."
fi

ESBMC_MD5="618f1fd89c399102865f9e366d164cb6"

if [ ! -f "bin/esbmc" ] || [ "$(md5sum bin/esbmc | awk '{ print $1 }')" != "$ESBMC_MD5" ]; then
  echo -e "\n#Downloading ESBMC"
  git lfs install
  git lfs pull
  chmod +x bin/esbmc
fi

# Clone the consensus repository
if [ ! -d "consensus-specs" ]; then
    echo "Cloning the consensus-specs repository..."
    git clone https://github.com/ethereum/consensus-specs.git
fi

# Create a virtual environment
python3 -m venv ethcheck_env

# Activate the virtual environment
source ethcheck_env/bin/activate

# Change to the cloned directory
pushd consensus-specs/
git checkout $CONSENSUS_RELEASE

# Install dependencies
pip install setuptools
pip install colorama
pip install ast2json
pip install pytest
pip install wheel

# Install the consensus project
python setup.py install

# Run consensus install tests
make install_test

python setup.py pyspecdev

popd
