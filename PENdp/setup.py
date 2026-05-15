from setuptools import setup, find_packages

setup(
    name="pendp",
    version="1.0.0",
    description="PENdp AI Peptide Design Platform",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "pandas>=2.0",
        "pyyaml>=6.0",
        "scikit-learn>=1.3",
    ],
    entry_points={
        "console_scripts": [
            "pendp=pendp.cli:main",
        ],
    },
)
