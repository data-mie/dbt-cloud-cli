import sys
import json
import time
import click
from dbt_cloud.job import DbtCloudJob, DbtCloudJobRunStatus, DbtCloudJobRunArgs


@click.group()
def dbt_cloud():
    pass


@dbt_cloud.group()
def job():
    pass


@job.command()
@DbtCloudJobRunArgs.click_options
@click.option(
    f"--wait/--no-wait",
    default=False,
    help="Wait for the process to finish before returning from the API call."
)
def run(wait, **kwargs):
    args = DbtCloudJobRunArgs(**kwargs)
    job = DbtCloudJob(**args.dict())
    response, job_run = job.run(args=args)
    if wait:
        while True:
            response, status = job_run.get_status()
            click.echo(f"Job {job.job_id} run {job_run.job_run_id}: {status.name} ...")
            if status == DbtCloudJobRunStatus.SUCCESS:
                break
            elif status in (DbtCloudJobRunStatus.ERROR, DbtCloudJobRunStatus.CANCELLED):
                raise Exception("Failure!")
            time.sleep(5)
    click.echo(json.dumps(response.json(), indent=2))