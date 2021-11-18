from setuptools import setup, find_packages

setup(
    name="dbt_cloud",
    version="0.1.0",
    description="dbt Cloud command line interface (CLI)",
    python_requires=">=3.6",
    packages=find_packages(),
    install_requires=["requests", "click", "pydantic"],
    extras_require={"test": ["pytest"]},
    scripts=[],
    entry_points={"console_scripts": ["dbt-cloud = dbt_cloud.cli:dbt_cloud"]},
)
