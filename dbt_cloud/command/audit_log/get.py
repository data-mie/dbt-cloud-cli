import requests
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudAuditLogGetCommand(DbtCloudAccountCommand):
    """Retrieves audit logs for the dbt Cloud account."""

    logged_at_start: Optional[str] = Field(
        description="Start date (YYYY-MM-DD) for the returned logs."
    )
    logged_at_end: Optional[str] = Field(
        description="End date (YYYY-MM-DD) for the returned logs."
    )
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Offset for the returned logs. Must be a positive integer.",
    )
    limit: Optional[int] = Field(
        100,
        ge=0,
        description="A limit on the number of logs to be returned. Must be a positive integer.",
    )
    _api_version: str = PrivateAttr("v3")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/audit-logs/"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params=self.get_payload(
                exclude=["api_token", "dbt_cloud_host", "account_id"]
            ),
        )
        return response
