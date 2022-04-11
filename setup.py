"""Package configuration."""
import pathlib

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

here = pathlib.Path(__file__).parent.resolve()


def get_version():
    with open(here / "src" / "sealevelrise" / "__init__.py", mode="r") as file:
        version_line = [
            line.strip() for line in file.readlines() if "__version__" in line
        ][0]
        return version_line.split("=")[-1].strip().strip('"')


setup(
    name="sealevelrise",
    version=get_version(),
    author="Jean O. Toilliez",
    author_email="jeantoilliez@gmail.com",
    description=(
        "Small utility for fetching, combining, and manipulating Sea Level Rise Projections"
        " from various sources for engineering calculations"
    ),
    url="https://github.com/jtoilliez/slr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=["numpy", "pandas", "matplotlib", "pathlib"],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "jupyter", "black", "wheel"]
    },
    include_package_data=True,
    keywords=[
        "sea level rise",
        "climate",
        "sustainability",
        "NOAA",
        "datums",
        "water",
        "risk",
        "asset management",
        "coastal",
        "ocean",
        "marine",
        "environmental",
        "engineering",
    ],
    project_urls={
        "GitHub": "https://github.com/jtoilliez/slr",
        "PyPI": "https://pypi.org/project/sealevelrise/",
    },
)
