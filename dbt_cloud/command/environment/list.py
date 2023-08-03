import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudProjectCommand
from dbt_cloud.field import LIMIT_FIELD, OFFSET_FIELD, DBT_VERSION_FIELD


class DbtCloudEnvironmentListCommand(DbtCloudProjectCommand):
    """Retrieves environments in a given project."""

    limit: Optional[int] = LIMIT_FIELD
    dbt_version: Optional[str] = DBT_VERSION_FIELD
    offset: Optional[int] = OFFSET_FIELD
    state: Optional[int] = Field(
        description="State of the environment. 1 = Active.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/environments"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={
                "limit": self.limit,
                "offset": self.offset,
                "dbt_version": self.dbt_version,
                "state": self.state,
            },
        )
        return response
