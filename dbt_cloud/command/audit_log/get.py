import requests
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudAuditLogGetCommand(DbtCloudAccountCommand):
    """Retrieves audit logs for the dbt Cloud account."""

    logged_at_start: str = Field(description="Start date for the returned logs.")
    logged_at_end: str = Field(description="End date for the returned logs.")
    offset: Optional[int] = Field(0, description="Offset for the returned logs.")
    limit: Optional[int] = Field(
        10, description="A limit on the number of logs to be returned."
    )
    _api_version: str = PrivateAttr("v3")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/audit-logs/"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
