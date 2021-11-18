import os
import time
import click
from dbt_cloud.job import DbtCloudJob, DbtCloudJobRunStatus


@click.group()
def dbt_cloud():
    pass


@dbt_cloud.group()
def job():
    pass


@job.command()
@click.option(
    "--cause",
    type=str,
    default="Triggered via API",
    help="A text description of the reason for running the job",
)
@click.option(
    "--git-sha",
    type=str,
    required=False,
    help="The git sha to check out before running the job",
)
@click.option(
    "--account-id",
    type=int,
    default=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
    help="dbt Cloud account ID",
)
@click.option(
    "--job-id",
    type=int,
    default=lambda: os.environ["DBT_CLOUD_JOB_ID"],
    help="dbt Cloud job ID",
)
@click.option(
    "--api-token",
    type=str,
    default=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
    help="dbt Cloud API token",
)
def run(cause: str, git_sha: str, account_id: int, job_id: int, api_token: str):
    job = DbtCloudJob(account_id=account_id, job_id=job_id, api_token=api_token)
    click.echo(f"Trigger dbt Cloud job {job.job_id}")
    job_run = job.run(cause=cause, git_sha=git_sha)
    click.echo(f"   - Job run ID: {job_run.job_run_id}")
    click.echo(f"   - Job run payload: {job_run.payload}")
    while True:
        time.sleep(5)
        status = job_run.get_status()
        click.echo(f"   - Job run status: {status.name}")
        if status == DbtCloudJobRunStatus.SUCCESS:
            break
        elif status in (DbtCloudJobRunStatus.ERROR, DbtCloudJobRunStatus.CANCELLED):
            raise Exception("Failure!")
    click.echo(f"dbt Cloud job run {job_run.job_run_id} finished!")
