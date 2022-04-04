import os
import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import JOB_ID_FIELD


class DbtCloudJobGetCommand(DbtCloudAccountCommand):
    """Returns the details of a dbt Cloud job."""

    job_id: int = JOB_ID_FIELD
    order_by: Optional[str] = Field(
        description="Field to order the result by. Use '-' to indicate reverse order."
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs/{self.job_id}"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"order_by": self.order_by},
        )
        return response
