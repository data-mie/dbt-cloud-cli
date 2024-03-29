import requests
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import LIMIT_FIELD


class DbtCloudJobListCommand(DbtCloudAccountCommand):
    """Returns a list of jobs in the account."""

    _api_version: str = PrivateAttr("v2")
    order_by: Optional[str] = Field(
        description="Field to order the result by. Use - to indicate reverse order."
    )
    limit: Optional[int] = LIMIT_FIELD
    project_id: Optional[str] = Field(description="Filter jobs by project ID.")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={
                "order_by": self.order_by,
                "project_id": self.project_id,
                "limit": self.limit,
            },
        )
        return response
