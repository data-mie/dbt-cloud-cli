import requests
from typing import Optional, List
from pydantic import Field, validator
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import JOB_ID_FIELD, PythonLiteralOption


class DbtCloudJobRunCommand(DbtCloudAccountCommand):
    """Triggers a dbt Cloud job run and returns a status JSON response."""

    job_id: int = JOB_ID_FIELD
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
        click_cls=PythonLiteralOption,
        description="Override the list of steps for this job",
    )

    @validator("steps_override")
    def check_steps_override_is_none_if_empty(cls, value):
        return value or None

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs/{self.job_id}/run/"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json=self.get_payload(),
        )
        return response
