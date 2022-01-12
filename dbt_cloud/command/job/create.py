import requests
from enum import Enum
from typing import Optional, List
from pydantic import Field
from dbt_cloud.command.command import DbtCloudCommand, DbtCloudBaseModel


class DateTypeEnum(Enum):
    EVERY_DAY = "every_day"
    DAYS_OF_WEEK = "days_of_week"
    CUSTOM_CRON = "custom_cron"


class TimeTypeEnum(Enum):
    EVERY_HOUR = "every_hour"
    AT_EXACT_HOURS = "at_exact_hours"


class DbtCloudJobTriggers(DbtCloudBaseModel):
    github_webhook: bool = Field(default=False)
    schedule: bool = Field(default=False)
    custom_branch_only: bool = Field(default=False)


class DbtCloudJobSettings(DbtCloudBaseModel):
    threads: int = Field(
        default=1,
        description="The maximum number of models to run in parallel in a single dbt run.",
    )
    target_name: str = Field(
        default="default",
        description=r"Informational field that can be consumed in dbt project code with {{ target.name }}.",
    )


class DbtCloudJobScheduleDate(DbtCloudBaseModel):
    type: DateTypeEnum = Field(default="every_day", description=None)


class DbtCloudJobScheduleTime(DbtCloudBaseModel):
    type: TimeTypeEnum = Field(default="every_hour", description=None)
    interval: int = Field(default=1)


class DbtCloudJobSchedule(DbtCloudBaseModel):
    cron: str = Field(
        default="0 * * * *", description="Cron-syntax schedule for the job."
    )
    date: DbtCloudJobScheduleDate = Field(default_factory=DbtCloudJobScheduleDate)
    time: DbtCloudJobScheduleTime = Field(default_factory=DbtCloudJobScheduleTime)


class DbtCloudJobCreateCommand(DbtCloudCommand):
    """Creates a job in a dbt Cloud project."""

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

    @property
    def api_url(self) -> str:
        api_url = f"{super().api_url}/jobs/"
        return api_url

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url, headers=self.request_headers, json=self.get_payload()
        )
        return response
