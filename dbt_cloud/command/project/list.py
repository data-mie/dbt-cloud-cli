import requests
from typing import Optional
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import LIMIT_FIELD, OFFSET_FIELD


class DbtCloudProjectListCommand(DbtCloudAccountCommand):
    """Returns a list of projects in the account."""

    limit: Optional[int] = LIMIT_FIELD
    offset: Optional[int] = OFFSET_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"limit": self.limit, "offset": self.offset},
        )
        return response
