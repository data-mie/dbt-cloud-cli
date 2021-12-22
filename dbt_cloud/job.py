import requests
import os
from enum import IntEnum, Enum
from typing import Optional, List, Tuple, Dict, Any, Literal
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


class DbtCloudJobTriggers(ArgsBaseModel):
    github_webhook: bool = Field(default=False)
    schedule: bool = Field(default=False)
    custom_branch_only: bool = Field(default=False)


class DbtCloudJobSettings(ArgsBaseModel):
    threads: int = Field(
        default=1,
        description="The maximum number of models to run in parallel in a single dbt run.",
    )
    target_name: str = Field(
        default="default",
        description=r"Informational field that can be consumed in dbt project code with {{ target.name }}.",
    )


class DateTypeEnum(Enum):
    EVERY_DAY = "every_day"
    DAYS_OF_WEEK = "days_of_week"
    CUSTOM_CRON = "custom_cron"


class TimeTypeEnum(Enum):
    EVERY_HOUR = "every_hour"
    AT_EXACT_HOURS = "at_exact_hours"


class DbtCloudJobScheduleDate(ArgsBaseModel):
    type: DateTypeEnum = Field(default="every_day", description=None)


class DbtCloudJobScheduleTime(ArgsBaseModel):
    type: TimeTypeEnum = Field(default="every_hour", description=None)
    interval: int = Field(default=1)


class DbtCloudJobSchedule(ArgsBaseModel):
    cron: str = Field(
        default="0 * * * *", description="Cron-syntax schedule for the job."
    )
    date: DbtCloudJobScheduleDate = Field(default_factory=DbtCloudJobScheduleDate)
    time: DbtCloudJobScheduleTime = Field(default_factory=DbtCloudJobScheduleTime)


class DbtCloudJobCreateArgs(DbtCloudArgsBaseModel):
    id: Optional[int] = Field(default=None, description="Must be empty.")
    project_id: int = Field(..., description="Numeric ID of the dbt Cloud project.")
    environment_id: int = Field(
        ..., description="Numeric ID of the dbt Cloud environment."
    )
    name: str = Field(..., description="A name for the job.")
    execute_steps: List[str] = Field(..., description="Job execution steps.")
    dbt_version: Optional[str] = Field(
        default=None,
        description="Overrides the dbt_version specified on the attached Environment if provided.",
    )
    triggers: Optional[DbtCloudJobTriggers] = Field(default_factory=DbtCloudJobTriggers)
    settings: Optional[DbtCloudJobSettings] = Field(default_factory=DbtCloudJobSettings)
    state: Optional[int] = Field(default=1, description="1 = active, 2 = deleted")
    generate_docs: Optional[bool] = Field(
        default=False,
        description="When true, run a dbt docs generate step at the end of runs triggered from this job.",
    )
    schedule: Optional[DbtCloudJobSchedule] = Field(default_factory=DbtCloudJobSchedule)

    def get_payload(self):
        return super().get_payload(exclude_keys=["api_token"])


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
    job_id: Optional[int]

    def get_api_url(self) -> str:
        if self.job_id is not None:
            return f"{super().get_api_url()}/jobs/{self.job_id}"
        return f"{super().get_api_url()}/jobs"

    def get(self, order_by: str) -> requests.Response:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
            params={"order_by": order_by},
        )
        response.raise_for_status()
        return response

    def create(self, args: DbtCloudJobCreateArgs) -> requests.Response:
        response = requests.post(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
            json=args.get_payload(),
        )
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
