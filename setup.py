from setuptools import setup, find_packages

setup(
    name="ethcheck",
    version="0.1.0",
    description="A Python tool for verifying Ethereum Consensus Specification using ESBMC",
    author="Bruno Farias",
    author_email="brunocarvalhofarias@gmail.com",
    url="https://github.com/brcfarias/ethcheck",
    packages=find_packages(),
    install_requires=[
        'colorama',
        'pytest',
        'ast2json',
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
