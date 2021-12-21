import requests
import os
from enum import IntEnum
from typing import Optional, List, Tuple, Dict, Any
from pydantic import Field
from dbt_cloud.account import DbtCloudAccount
from dbt_cloud.args import ArgsBaseModel


class DbtCloudRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudArgsBaseModel(ArgsBaseModel):
    api_token: str = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
        description="API authentication key (default: 'DBT_CLOUD_API_TOKEN' environment variable)",
    )
    account_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
        description="Numeric ID of the Account that the job belongs to (default: 'DBT_CLOUD_ACCOUNT_ID' environment variable)",
    )


class DbtCloudRunArgs(DbtCloudArgsBaseModel):
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


class DbtCloudJobGetArgs(DbtCloudArgsBaseModel):
    job_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
        description="Numeric ID of the job to run (default: 'DBT_CLOUD_JOB_ID' environment variable)",
    )
    order_by: Optional[str] = Field(
        description="Field to order the result by. Use '-' to indicate reverse order."
    )


class DbtCloudRunGetArgs(DbtCloudArgsBaseModel):
    run_id: int = Field(
        ...,
        description="Numeric ID of the run",
    )
    include_related: Optional[List[str]] = Field(
        description="List of related fields to pull with the run. Valid values are 'trigger', 'job', and 'debug_logs'. If 'debug_logs' is not provided in a request, then the included debug logs will be truncated to the last 1,000 lines of the debug log output file.",
    )

    def get_run(self) -> "DbtCloudRun":
        return DbtCloudRun(
            run_id=self.run_id, api_token=self.api_token, account_id=self.account_id
        )


class DbtCloudJob(DbtCloudAccount):
    job_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/jobs/{self.job_id}"

    def get(self, order_by: str) -> requests.Response:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
            params={"order_by": order_by},
        )
        response.raise_for_status()
        return response

    def run(self, args: DbtCloudRunArgs) -> Tuple[requests.Response, "DbtCloudRun"]:
        """
        :returns: Job run ID
        """
        response = requests.post(
            url=f"{self.get_api_url()}/run/",
            headers={"Authorization": f"Token {self.api_token}"},
            json=args.get_payload(),
        )
        response.raise_for_status()
        run_id = response.json()["data"]["id"]
        return response, DbtCloudRun(
            run_id=run_id,
            args=args,
            account_id=self.account_id,
            api_token=self.api_token,
        )


class DbtCloudRun(DbtCloudAccount):
    run_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.run_id}"

    def get_status(self) -> Tuple[requests.Response, DbtCloudRunStatus]:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        return response, DbtCloudRunStatus(response.json()["data"]["status"])
