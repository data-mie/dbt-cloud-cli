# dbt-cloud-cli

This is a work a in progress for a dbt Cloud command line interface!

## Installing the CLI

From GitHub:

    pip install git+https://github.com/data-mie/dbt-cloud-cli.git

From PyPI (not yet available):

    pip install dbt-cloud-cli

## Commands

Add a `--help` flag at the end of any of the listed commands for full command documentation (e.g., `dbt-cloud job run --help`).

| Command | Description | Usage example | dbt Cloud API endpoint
| --- | --- | --- | --- |
| `dbt-cloud job run` | Kick off a run for a job | `dbt-cloud job run --job-id 12345 --account-id 12345 --cause "Triggered via API" --git-sha foobar123` | https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun |
