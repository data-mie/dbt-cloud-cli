import os
import logging
import time
import click
from dbt_cloud.args import DbtCloudArgsBaseModel, translate_click_options
from dbt_cloud.job import (
    DbtCloudJob,
    DbtCloudJobArgs,
    DbtCloudJobRunArgs,
    DbtCloudJobGetArgs,
    DbtCloudJobCreateArgs,
)
from dbt_cloud.run import (
    DbtCloudRunStatus,
    DbtCloudRunGetArgs,
    DbtCloudRunListArtifactsArgs,
    DbtCloudRunGetArtifactArgs,
)
from dbt_cloud.serde import json_to_dict, dict_to_json
from dbt_cloud.exc import DbtCloudException


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


@job.command(help="Triggers a dbt Cloud job run and returns a status JSON response.")
@DbtCloudJobRunArgs.click_options
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
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudJobRunArgs(**kwargs_translated)
    job = args.get_job()
    response, run = job.run(args=args)
    if wait:
        while True:
            response, status = run.get_status()
            click.echo(f"Job {job.job_id} run {run.run_id}: {status.name} ...")
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


@job.command(help="Returns the details of a dbt Cloud job.")
@DbtCloudJobGetArgs.click_options
def get(**kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudJobGetArgs(**kwargs_translated)
    job = DbtCloudJob(**args.dict())
    response = job.get(order_by=args.order_by)
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job.command(help="Creates a job in a dbt Cloud project.")
@DbtCloudJobCreateArgs.click_options
def create(**kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudJobCreateArgs(**kwargs_translated)
    job = DbtCloudJob(job_id=None, **args.dict())
    response = job.create(args)
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job.command(help="Deletes a job from a dbt Cloud project.")
@DbtCloudJobArgs.click_options
def delete(**kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudJobArgs(**kwargs_translated)
    job = args.get_job()
    response = job.delete()
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job.command(help="Exports a dbt Cloud job as JSON to a file.")
@DbtCloudJobArgs.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Export file path.",
)
def export(file, **kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudJobArgs(**kwargs_translated)
    job = args.get_job()
    exclude = ["id"]
    file.write(job.to_json(exclude=exclude))


@job.command(help="Imports a dbt Cloud job from exported JSON.", name="import")
@DbtCloudArgsBaseModel.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("r"),
    help="Import file path.",
)
def import_job(file, **kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudArgsBaseModel(**kwargs_translated)
    job_create_kwargs = json_to_dict(file.read())
    job_create_args = DbtCloudJobCreateArgs(**job_create_kwargs)
    job = DbtCloudJob(job_id=None, **args.dict())
    response = job.create(job_create_args)
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job_run.command(help="Prints a dbt Cloud run status JSON response.")
@DbtCloudRunGetArgs.click_options
def get(**kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudRunGetArgs(**kwargs_translated)
    run = args.get_run()
    response, _ = run.get_status()
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job_run.command(help="Fetches a list of artifact files generated for a completed run.")
@DbtCloudRunListArtifactsArgs.click_options
def list_artifacts(**kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudRunListArtifactsArgs(**kwargs_translated)
    run = args.get_run()
    response = run.list_artifacts(step=args.step)
    click.echo(dict_to_json(response.json()))
    response.raise_for_status()


@job_run.command(help="Fetches an artifact file from a completed run.")
@DbtCloudRunGetArtifactArgs.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("wb"),
    help="Export file path.",
)
def get_artifact(file, **kwargs):
    kwargs_translated = translate_click_options(**kwargs)
    args = DbtCloudRunGetArtifactArgs(**kwargs_translated)
    run = args.get_run()
    response = run.get_artifact(path=args.path, step=args.step)
    file.write(response.content)
    response.raise_for_status()
