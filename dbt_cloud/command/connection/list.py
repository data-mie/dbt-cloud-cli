import requests
from typing import Optional
from dbt_cloud.command.command import DbtCloudProjectCommand
from dbt_cloud.field import LIMIT_FIELD, OFFSET_FIELD, PROJECT_ID_FIELD


class DbtCloudConnectionListCommand(DbtCloudProjectCommand):
    """Retrievies details of dbt Cloud database connections in a given project."""

    limit: Optional[int] = LIMIT_FIELD
    offset: Optional[int] = OFFSET_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/connections/"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"limit": self.limit, "offset": self.offset},
        )
        return response
