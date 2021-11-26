from pathlib import Path
from setuptools import setup


README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="dbt-cloud-cli",
    version="0.1.0",
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
    packages=["dbt_cloud"],
    install_requires=["requests", "click", "pydantic"],
    extras_require={"test": ["pytest"]},
    scripts=[],
    entry_points={"console_scripts": ["dbt-cloud = dbt_cloud.cli:dbt_cloud"]},
)
