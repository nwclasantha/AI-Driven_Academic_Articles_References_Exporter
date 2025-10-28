#!/usr/bin/env python3
"""
Setup script for IEEE Reference Extractor - Enterprise Edition
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="ieee-reference-extractor",
    version="3.0.0",
    author="IEEE Reference Extractor Team",
    description="Enterprise-level reference extraction from IEEE academic papers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.6.0",
        "qt-material>=2.14",
        "PyMuPDF>=1.23.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
            "mypy>=1.4.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ieee-extractor=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ieee, references, bibliography, bibtex, academic, research, pdf",
)
