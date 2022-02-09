import os
import logging
import time
import click
import ast
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
    DbtCloudRunListCommand,
    DbtCloudJobListCommand,
    DbtCloudProjectListCommand,
)
from dbt_cloud.demo import data_catalog
from dbt_cloud.serde import json_to_dict, dict_to_json
from dbt_cloud.exc import DbtCloudException


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)


def execute_and_print(command, **kwargs):
    response = command.execute(**kwargs)
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


@dbt_cloud.group(help="dbt Cloud job commands")
def job():
    pass


@dbt_cloud.group(name="run", help="dbt Cloud run commands")
def job_run():
    pass


@dbt_cloud.group(help="dbt Cloud project commands")
def project():
    pass


@dbt_cloud.group(help="dbt Cloud Metadata API commands")
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


@job.command(help=DbtCloudJobListCommand.get_description())
@DbtCloudJobListCommand.click_options
def list(**kwargs):
    command = DbtCloudJobListCommand.from_click_options(**kwargs)
    execute_and_print(command)


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


@job.command(help="Delete all jobs on the account.")
@DbtCloudJobListCommand.click_options
@click.option(
    "--keep-jobs",
    cls=PythonLiteralOption,
    default=[],
    help="List of job IDs to exclude from deletion.",
)
@click.option("--dry-run", is_flag=True, help="Execute as a dry run.")
@click.option(
    "-y", "--yes", "assume_yes", is_flag=True, help="Automatic yes to prompts."
)
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Response export file path.",
)
def delete_all(keep_jobs, dry_run, file, assume_yes, **kwargs):
    list_command = DbtCloudJobListCommand.from_click_options(**kwargs)
    response = list_command.execute()
    response.raise_for_status()
    job_ids_to_delete = [
        job_dict["id"]
        for job_dict in response.json()["data"]
        if job_dict["id"] not in keep_jobs
    ]
    click.echo(f"Jobs to delete: {job_ids_to_delete}")
    deleted_job_responses = []
    if not dry_run:
        for job_id in job_ids_to_delete:
            delete_command = DbtCloudJobDeleteCommand(**kwargs, job_id=job_id)
            if assume_yes:
                is_confirmed = True
            else:
                is_confirmed = click.confirm(f"Delete job {job_id}?")
            if is_confirmed:
                response = delete_command.execute()
                response.raise_for_status()
                deleted_job_responses.append(response.json())
                click.echo(f"Job {job_id} was deleted.")
    file.write(dict_to_json(deleted_job_responses))


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


@job_run.command(help=DbtCloudRunListCommand.get_description())
@DbtCloudRunListCommand.click_options
def list(**kwargs):
    command = DbtCloudRunListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)
    if command.paginate:
        pagination_token = response.headers.get("X-Dbt-Continuation-Token")
        while pagination_token is not None:
            response = execute_and_print(command, pagination_token=pagination_token)
            pagination_token = response.headers.get("X-Dbt-Continuation-Token")


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


@project.command(help=DbtCloudProjectListCommand.get_description())
@DbtCloudProjectListCommand.click_options
def list(**kwargs):
    command = DbtCloudProjectListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


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
    command = DbtCloudMetadataQueryCommand.from_click_options(
        query=file.read(), **kwargs
    )
    execute_and_print(command)


@dbt_cloud.group(help="Demo applications")
def demo():
    pass


demo.add_command(data_catalog)
