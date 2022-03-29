"""Package configuration."""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slr",
    version="0.1",
    author="Jean O. Toilliez",
    author_email="JNOT@COWI",
    description=(
        "Small utility for manipulating Sea Level Rise Projections"
        " for engineering calculations"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=["numpy", "pandas", "matplotlib", "pathlib"],
    extras_requires={"dev": ["pytest", "pytest-cov", "flake8", "jupyter", "black"]},
)
