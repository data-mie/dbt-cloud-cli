import json
import time
import click
from dbt_cloud.job import (
    DbtCloudJob,
    DbtCloudRunStatus,
    DbtCloudRunArgs,
    DbtCloudJobGetArgs,
    DbtCloudRunGetArgs,
)
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


@job.command()
@DbtCloudRunArgs.click_options
@click.option(
    f"--wait/--no-wait",
    default=False,
    help="Wait for the process to finish before returning from the API call.",
)
def run(wait, **kwargs):
    args = DbtCloudRunArgs(**kwargs)
    job = DbtCloudJob(**args.dict())
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


@job.command()
@DbtCloudJobGetArgs.click_options
def get(**kwargs):
    args = DbtCloudJobGetArgs(**kwargs)
    job = DbtCloudJob(**args.dict())
    response = job.get(order_by=args.order_by)
    click.echo(json.dumps(response.json(), indent=2))


@job_run.command()
@DbtCloudRunGetArgs.click_options
def get(**kwargs):
    args = DbtCloudRunGetArgs(**kwargs)
    run = args.get_run()
    response, _ = run.get_status()
    click.echo(json.dumps(response.json(), indent=2))
