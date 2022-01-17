import requests
from enum import Enum
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudRunStatus(Enum):
    QUEUED = "Queued"
    STARTING = "Starting"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"


class DbtCloudRunListCommand(DbtCloudCommand):
    """Returns a list of runs in the account. The runs are returned sorted by creation date, with the most recent run appearing first."""

    limit: Optional[int] = Field(
        100,
        gte=1,
        lte=100,
        description="A limit on the number of objects to be returned, between 1 and 100.",
    )
    environment_id: Optional[str] = Field(description="Filter runs by environment ID.")
    project_id: Optional[str] = Field(description="Filter runs by project ID.")
    job_id: Optional[str] = Field(description="Filter runs by job ID.")
    status: Optional[DbtCloudRunStatus] = Field(description="Filter by run status.")
    _api_version: str = PrivateAttr("v4")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={
                "limit": self.limit,
                "environment": self.environment_id,
                "project": self.project_id,
                "job": self.job_id,
                "status": self.status,
            },
        )
        return response
