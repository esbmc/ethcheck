from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "pip-description.md").read_text()

setup(
    name="ethcheck",
    version="0.1.2",
    description="A Python tool for verifying Ethereum Consensus Specification using ESBMC",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Bruno Farias",
    author_email="brunocarvalhofarias@gmail.com",
    url="https://github.com/esbmc/ethcheck",
    packages=find_packages(),
    install_requires=[
        'colorama',
        'pytest',
        'ast2json',
        'setuptools',
        # List other dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'ethcheck=ethcheck.ethcheck:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['bin/esbmc'],
    },
    data_files=[
        ('bin', ['bin/esbmc']),
    ],
)
