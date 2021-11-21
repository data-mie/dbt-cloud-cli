import requests
import os
from enum import IntEnum
from typing import Optional, List
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


class DbtCloudJob(DbtCloudAccount):
    job_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/jobs/{self.job_id}"

    def run(self, cause: str, git_sha: str) -> "DbtCloudJobRun":
        """
        :returns: Job run ID
        """
        payload = {"cause": cause}
        if git_sha:
            payload["git_sha"] = git_sha

        response = requests.post(
            url=f"{self.get_api_url()}/run/",
            headers={"Authorization": f"Token {self.api_token}"},
            json=payload,
        )
        response.raise_for_status()

        response_payload = response.json()
        job_run_id = response_payload["data"]["id"]
        return DbtCloudJobRun(
            job_run_id=job_run_id,
            payload=payload,
            account_id=self.account_id,
            api_token=self.api_token,
        )


class DbtCloudJobRunArgs(ArgsBaseModel):
    api_token: str = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
        description="API authentication key",
    )
    account_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
        description="Numeric ID of the Account that the job belongs to",
    )
    job_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
        description="Numeric ID of the job to run",
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


class DbtCloudJobRun(DbtCloudAccount):
    job_run_id: int
    payload: Optional[dict]

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.job_run_id}"

    def get_status(self) -> DbtCloudJobRunStatus:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        response_payload = response.json()
        return DbtCloudJobRunStatus(response_payload["data"]["status"])
