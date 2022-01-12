import os
import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudCommand
from dbt_cloud.field import JOB_ID_FIELD


class DbtCloudJobGetCommand(DbtCloudCommand):
    """Returns the details of a dbt Cloud job."""

    job_id: int = JOB_ID_FIELD
    order_by: Optional[str] = Field(
        description="Field to order the result by. Use '-' to indicate reverse order."
    )

    @property
    def api_url(self) -> str:
        api_url = f"{super().api_url}/jobs"
        if self.job_id is not None:
            api_url = f"{api_url}/{self.job_id}"
        return api_url

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"order_by": self.order_by},
        )
        return response
