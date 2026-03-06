import requests
from enum import Enum
from typing import Optional, List
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand, ClickBaseModel
from dbt_cloud.field import PythonLiteralOption, PROJECT_ID_FIELD, ENVIRONMENT_ID_FIELD


class DateTypeEnum(Enum):
    EVERY_DAY = "every_day"
    DAYS_OF_WEEK = "days_of_week"
    CUSTOM_CRON = "custom_cron"


class TimeTypeEnum(Enum):
    EVERY_HOUR = "every_hour"
    AT_EXACT_HOURS = "at_exact_hours"


class JobTypeEnum(str, Enum):
    CI = "ci"
    SCHEDULED = "scheduled"
    OTHER = "other"
    MERGE = "merge"
    ADAPTIVE = "adaptive"
    EXPOSURE_SYNC = "exposure_sync"


class DbtCloudJobTriggers(ClickBaseModel):
    github_webhook: bool = Field(default=False)
    schedule: bool = Field(default=False)
    custom_branch_only: bool = Field(default=False)
    git_provider_webhook: bool = Field(default=False)
    on_merge: bool = Field(default=False)


class DbtCloudJobSettings(ClickBaseModel):
    threads: int = Field(
        default=1,
        description="The maximum number of models to run in parallel in a single dbt run.",
    )
    target_name: str = Field(
        default="default",
        description=r"Informational field that can be consumed in dbt project code with {{ target.name }}.",
    )


class DbtCloudJobExecution(ClickBaseModel):
    timeout_seconds: int = Field(
        default=0,
        description="Maximum execution time in seconds. 0 means no timeout.",
    )


class DbtCloudJobScheduleDate(ClickBaseModel):
    type: DateTypeEnum = Field(default=DateTypeEnum.EVERY_DAY, description=None)


class DbtCloudJobScheduleTime(ClickBaseModel):
    type: TimeTypeEnum = Field(default=TimeTypeEnum.EVERY_HOUR, description=None)
    interval: int = Field(default=1)


class DbtCloudJobSchedule(ClickBaseModel):
    cron: str = Field(
        default="0 * * * *", description="Cron-syntax schedule for the job."
    )
    date: DbtCloudJobScheduleDate = Field(default_factory=DbtCloudJobScheduleDate)
    time: DbtCloudJobScheduleTime = Field(default_factory=DbtCloudJobScheduleTime)


class DbtCloudJobCreateCommand(DbtCloudAccountCommand):
    """Creates a job in a dbt Cloud project."""

    _api_version: str = PrivateAttr("v2")

    id: Optional[int] = Field(
        default=None,
        json_schema_extra={"exclude_from_click_options": True},
        description="Assigned by the dbt Cloud API. Cannot be overridden.",
    )
    project_id: int = PROJECT_ID_FIELD
    environment_id: int = ENVIRONMENT_ID_FIELD
    name: str = Field(..., description="A name for the job.")
    execute_steps: List[str] = Field(
        ...,
        json_schema_extra={"click_cls": PythonLiteralOption},
        description="Job execution steps.",
    )
    dbt_version: Optional[str] = Field(
        default=None,
        description="Overrides the dbt_version specified on the attached Environment if provided.",
    )
    description: Optional[str] = Field(
        default=None,
        description="A description for the job.",
    )
    job_type: Optional[JobTypeEnum] = Field(
        default=None,
        description="The type of job. Valid values are ci, scheduled, other, merge, adaptive, exposure_sync.",
    )
    triggers: Optional[DbtCloudJobTriggers] = Field(default_factory=DbtCloudJobTriggers)
    settings: Optional[DbtCloudJobSettings] = Field(default_factory=DbtCloudJobSettings)
    execution: DbtCloudJobExecution = Field(default_factory=DbtCloudJobExecution)
    state: Optional[int] = Field(default=1, description="1 = active, 2 = deleted")
    generate_docs: Optional[bool] = Field(
        default=False,
        description="When true, run a dbt docs generate step at the end of runs triggered from this job.",
    )
    schedule: Optional[DbtCloudJobSchedule] = Field(default_factory=DbtCloudJobSchedule)
    deferring_job_definition_id: Optional[int] = Field(
        default=None,
        description="The ID of the job to defer to.",
    )
    deferring_environment_id: Optional[int] = Field(
        default=None,
        description="The ID of the environment to defer to.",
    )
    run_generate_sources: bool = Field(
        default=False,
        description="When true, run a dbt source freshness step at the start of runs triggered from this job.",
    )
    run_compare_changes: bool = Field(
        default=False,
        description="When true, compare changes between the current run and the previous run.",
    )
    run_lint: bool = Field(
        default=False,
        description="When true, run dbt lint as part of runs triggered from this job.",
    )
    errors_on_lint_failure: bool = Field(
        default=False,
        description="When true, fail the run if dbt lint reports errors.",
    )
    lifecycle_webhooks: bool = Field(
        default=False,
        description="When true, send lifecycle webhooks for runs triggered from this job.",
    )
    triggers_on_draft_pr: bool = Field(
        default=False,
        description="When true, CI jobs are also triggered by draft pull requests.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs/"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json=self.get_payload(),
            timeout=self.timeout,
        )
        return response
