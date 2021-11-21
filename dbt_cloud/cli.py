import os
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
def run(**kwargs):
    args = DbtCloudJobRunArgs(**kwargs)
    job = DbtCloudJob(**args.dict())
    click.echo(f"Trigger dbt Cloud job {job.job_id}")
    job_run = job.run(args=args)
    click.echo(f"   - Job run ID: {job_run.job_run_id}")
    click.echo(f"   - Job run payload: {args.get_payload()}")
    while True:
        time.sleep(5)
        status = job_run.get_status()
        click.echo(f"   - Job run status: {status.name}")
        if status == DbtCloudJobRunStatus.SUCCESS:
            break
        elif status in (DbtCloudJobRunStatus.ERROR, DbtCloudJobRunStatus.CANCELLED):
            raise Exception("Failure!")
    click.echo(f"dbt Cloud job run {job_run.job_run_id} finished!")
