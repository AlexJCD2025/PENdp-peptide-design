from setuptools import setup, find_packages

setup(
    name="pendp",
    version="4.4.0",
    description="PENdp AI Peptide Design Platform",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "pandas>=2.0",
        "pyyaml>=6.0",
        "scikit-learn>=1.3",
    ],
    extras_require={
        # ESM-2 embeddings (D7) — heavy; only needed for `--esm`
        "esm": ["torch>=2.0", "transformers>=4.30"],
        # Structural / QSAR refinement — RDKit is pip-installable; OpenMM
        # and ESMFold weights must be installed separately (conda/manual).
        "struct": ["rdkit>=2023.3"],
    },
    entry_points={
        "console_scripts": [
            "pendp=pendp.cli:main",
        ],
    },
)
