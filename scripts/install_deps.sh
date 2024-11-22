#!/bin/bash

CONSENSUS_RELEASE="v1.5.0-alpha.4"

# Function to check if a package is installed
is_package_installed() {
    dpkg -s "$1" &>/dev/null
}

# Check if git-lfs is installed
if ! is_package_installed git-lfs; then
    echo -e "# Installing git-lfs package"
    sudo apt install -y git-lfs
fi

if ! is_package_installed python3-venv; then
    echo -e "\n# Installing python3-venv"
    sudo apt install -y python3-venv
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
