import os
import logging
import time
import click
from dbt_cloud import DbtCloudRunStatus
from dbt_cloud.command import (
    DbtCloudJobGetCommand,
    DbtCloudJobCreateCommand,
    DbtCloudJobDeleteCommand,
    DbtCloudJobRunCommand,
    DbtCloudCommand,
    DbtCloudRunGetCommand,
    DbtCloudRunListArtifactsCommand,
    DbtCloudRunGetArtifactCommand,
    DbtCloudMetadataQueryCommand,
)
from dbt_cloud.serde import json_to_dict, dict_to_json
from dbt_cloud.exc import DbtCloudException


def execute_and_print(command):
    response = command.execute()
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()
    return response


@click.group()
def dbt_cloud():
    import http.client as http_client

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level)
    requests_logger = logging.getLogger("requests.packages.urllib3")
    requests_logger.setLevel(level)
    requests_logger.propagate = True
    if level == "DEBUG":
        http_client.HTTPConnection.debuglevel = 1


@dbt_cloud.group()
def job():
    pass


@dbt_cloud.group(name="run")
def job_run():
    pass


@dbt_cloud.group()
def metadata():
    pass


@job.command(help=DbtCloudJobRunCommand.get_description())
@DbtCloudJobRunCommand.click_options
@click.option(
    f"--wait/--no-wait",
    default=False,
    help="Wait for the process to finish before returning from the API call.",
)
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Response export file path.",
)
def run(wait, file, **kwargs):
    command = DbtCloudJobRunCommand.from_click_options(**kwargs)
    response = command.execute()

    if wait:
        run_id = response.json()["data"]["id"]
        while True:
            run_get_command = DbtCloudRunGetCommand(
                api_token=command.api_token,
                account_id=command.account_id,
                run_id=run_id,
            )
            response = run_get_command.execute()
            status = DbtCloudRunStatus(response.json()["data"]["status"])
            click.echo(f"Job {command.job_id} run {run_id}: {status.name} ...")
            if status == DbtCloudRunStatus.SUCCESS:
                break
            elif status in (DbtCloudRunStatus.ERROR, DbtCloudRunStatus.CANCELLED):
                href = response.json()["data"]["href"]
                raise DbtCloudException(
                    f"Job run failed with {status.name} status. For more information, see {href}."
                )
            time.sleep(5)

    file.write(dict_to_json(response.json()))
    response.raise_for_status()


@job.command(help=DbtCloudJobGetCommand.get_description())
@DbtCloudJobGetCommand.click_options
def get(**kwargs):
    command = DbtCloudJobGetCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help=DbtCloudJobCreateCommand.get_description())
@DbtCloudJobCreateCommand.click_options
def create(**kwargs):
    command = DbtCloudJobCreateCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help=DbtCloudJobDeleteCommand.get_description())
@DbtCloudJobDeleteCommand.click_options
def delete(**kwargs):
    command = DbtCloudJobDeleteCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help="Exports a dbt Cloud job as JSON to a file.")
@DbtCloudJobGetCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Export file path.",
)
def export(file, **kwargs):
    command = DbtCloudJobGetCommand.from_click_options(**kwargs)
    response = command.execute()
    response.raise_for_status()
    job_dict = response.json()["data"]
    job_dict.pop("id")
    file.write(dict_to_json(job_dict))


@job.command(help="Imports a dbt Cloud job from exported JSON.", name="import")
@DbtCloudCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("r"),
    help="Import file path.",
)
def import_job(file, **kwargs):
    base_command = DbtCloudCommand.from_click_options(**kwargs)
    job_create_kwargs = {**json_to_dict(file.read()), **base_command.dict()}
    command = DbtCloudJobCreateCommand(**job_create_kwargs)
    response = command.execute()
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job_run.command(help=DbtCloudRunGetCommand.get_description())
@DbtCloudRunGetCommand.click_options
def get(**kwargs):
    command = DbtCloudRunGetCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job_run.command(help=DbtCloudRunListArtifactsCommand.get_description())
@DbtCloudRunListArtifactsCommand.click_options
def list_artifacts(**kwargs):
    command = DbtCloudRunListArtifactsCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job_run.command(help=DbtCloudRunGetArtifactCommand.get_description())
@DbtCloudRunGetArtifactCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("wb"),
    help="Export file path.",
)
def get_artifact(file, **kwargs):
    command = DbtCloudRunGetArtifactCommand.from_click_options(**kwargs)
    response = command.execute()
    file.write(response.content)
    response.raise_for_status()


@metadata.command(help=DbtCloudMetadataQueryCommand.get_description())
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("r"),
    help="Read query from file.",
)
@DbtCloudMetadataQueryCommand.click_options
def query(file, **kwargs):
    command = DbtCloudMetadataQueryCommand.from_click_options(**kwargs)
    command._query = file.read()
    execute_and_print(command)
