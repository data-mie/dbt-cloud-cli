import requests
import os
from enum import IntEnum
from typing import Optional, List, Tuple, Dict, Any
from pydantic import Field
from dbt_cloud.account import DbtCloudAccount
from dbt_cloud.args import ArgsBaseModel


class DbtCloudJobRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudJobRunArgs(ArgsBaseModel):
    api_token: str = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
        description="API authentication key (default: 'DBT_CLOUD_API_TOKEN' environment variable)",
    )
    account_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
        description="Numeric ID of the Account that the job belongs to (default: 'DBT_CLOUD_ACCOUNT_ID' environment variable)",
    )
    job_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
        description="Numeric ID of the job to run (default: 'DBT_CLOUD_JOB_ID' environment variable)",
    )
    cause: str = Field(
        default="Triggered via API",
        description="A text description of the reason for running this job",
    )
    git_sha: Optional[str] = Field(
        description="The git sha to check out before running this job"
    )
    git_branch: Optional[str] = Field(
        description="The git branch to check out before running this job"
    )
    schema_override: Optional[str] = Field(
        description="Override the destination schema in the configured target for this job"
    )
    dbt_version_override: Optional[str] = Field(
        description="Override the version of dbt used to run this job"
    )
    threads_override: Optional[int] = Field(
        description="Override the number of threads used to run this job"
    )
    target_name_override: Optional[str] = Field(
        description="Override the target.name context variable used when running this job"
    )
    generate_docs_override: Optional[bool] = Field(
        description="Override whether or not this job generates docs (true=yes, false=no)"
    )
    timeout_seconds_override: Optional[int] = Field(
        description="Override the timeout in seconds for this job"
    )
    steps_override: Optional[List[str]] = Field(
        description="Override the list of steps for this job"
    )


class DbtCloudJob(DbtCloudAccount):
    job_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/jobs/{self.job_id}"

    def run(self, args: DbtCloudJobRunArgs) -> Tuple[requests.Response, "DbtCloudJobRun"]:
        """
        :returns: Job run ID
        """
        response = requests.post(
            url=f"{self.get_api_url()}/run/",
            headers={"Authorization": f"Token {self.api_token}"},
            json=args.get_payload(),
        )
        response.raise_for_status()
        job_run_id = response.json()["data"]["id"]
        return response, DbtCloudJobRun(
            job_run_id=job_run_id,
            args=args,
            account_id=self.account_id,
            api_token=self.api_token,
        )


class DbtCloudJobRun(DbtCloudAccount):
    job_run_id: int
    args: DbtCloudJobRunArgs

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.job_run_id}"

    def get_status(self) -> Tuple[requests.Response, DbtCloudJobRunStatus]:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        return response, DbtCloudJobRunStatus(response.json()["data"]["status"])
