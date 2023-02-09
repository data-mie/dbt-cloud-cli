from pathlib import Path
from setuptools import setup, find_packages


README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="dbt-cloud-cli",
    version="0.7.4",
    description="dbt Cloud command line interface (CLI)",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/data-mie/dbt-cloud-cli",
    author="Simo Tumelius",
    author_email="simo@datamie.fi",
    license="Apache Software License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
    packages=find_packages(exclude=("tests",)),
    install_requires=["requests", "click", "pydantic", "mergedeep"],
    extras_require={
        "test": ["pytest", "pytest-cov", "pytest-datadir", "requests-mock"],
        "lint": ["black"],
        "demo": ["inquirer", "art"],
    },
    scripts=[],
    entry_points={"console_scripts": ["dbt-cloud = dbt_cloud.cli:dbt_cloud"]},
)
