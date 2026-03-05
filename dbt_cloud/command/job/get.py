import requests
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import JOB_ID_FIELD


class DbtCloudJobGetCommand(DbtCloudAccountCommand):
    """Returns the details of a dbt Cloud job."""

    _api_version: str = PrivateAttr("v2")
    job_id: int = JOB_ID_FIELD
    include_related: Optional[str] = Field(
        default=None,
        description="Comma-separated list of related objects to include in the response. Valid values are environment, custom_environment_variables, most_recent_run, most_recent_completed_run.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs/{self.job_id}"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"include_related": self.include_related},
        )
        return response
