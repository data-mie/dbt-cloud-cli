import json
import time
import click
from pathlib import Path
from dbt_cloud.args import DbtCloudArgsBaseModel
from dbt_cloud.job import (
    DbtCloudJob,
    DbtCloudJobArgs,
    DbtCloudJobRunArgs,
    DbtCloudJobGetArgs,
    DbtCloudJobCreateArgs,
)
from dbt_cloud.run import DbtCloudRunStatus, DbtCloudRunGetArgs
from dbt_cloud.serde import json_to_dict
from dbt_cloud.exc import DbtCloudException


@click.group()
def dbt_cloud():
    pass


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
def run(wait, **kwargs):
    args = DbtCloudJobRunArgs(**kwargs)
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
    click.echo(json.dumps(response.json(), indent=2))
    response.raise_for_status()


@job.command(help="Returns the details of a dbt Cloud job.")
@DbtCloudJobGetArgs.click_options
def get(**kwargs):
    args = DbtCloudJobGetArgs(**kwargs)
    job = DbtCloudJob(**args.dict())
    response = job.get(order_by=args.order_by)
    click.echo(json.dumps(response.json(), indent=2))
    response.raise_for_status()


@job.command(help="creates a job in a dbt Cloud project.")
@DbtCloudJobCreateArgs.click_options
def create(**kwargs):
    args = DbtCloudJobCreateArgs(**kwargs)
    job = DbtCloudJob(job_id=None, **args.dict())
    response = job.create(args)
    click.echo(json.dumps(response.json(), indent=2))
    response.raise_for_status()


@job.command(help="Export job to a JSON file.")
@DbtCloudJobArgs.click_options
@click.option(
    "-f",
    "--file",
    required=True,
    type=Path,
    help="Export file path.",
)
def export(file, **kwargs):
    args = DbtCloudJobArgs(**kwargs)
    job = args.get_job()
    job.to_json(file)
    click.echo(f"Job {job.job_id} successfully exported to {file}")


@job.command(help="Import job from a JSON file to a dbt Cloud project.", name="import")
@DbtCloudArgsBaseModel.click_options
@click.option(
    "-f",
    "--file",
    required=True,
    type=Path,
    help="Import file path.",
)
def import_job(file, **kwargs):
    args = DbtCloudArgsBaseModel(**kwargs)
    job_create_kwargs = json_to_dict(file.read_text())
    job_create_args = DbtCloudJobCreateArgs(**job_create_kwargs)
    job = DbtCloudJob(job_id=job_create_kwargs["id"], **args.dict())
    # FIXME: Object of type DateTypeEnum is not JSON serializable
    job.create(job_create_args)


@job_run.command()
@DbtCloudRunGetArgs.click_options
def get(**kwargs):
    args = DbtCloudRunGetArgs(**kwargs)
    run = args.get_run()
    response, _ = run.get_status()
    click.echo(json.dumps(response.json(), indent=2))
    response.raise_for_status()
