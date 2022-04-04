from multiprocessing.sharedctypes import Value
import requests
from enum import Enum
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudRunStatus(Enum):
    QUEUED = "Queued"
    STARTING = "Starting"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"


class DbtCloudRunListCommand(DbtCloudAccountCommand):
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
    paginate: Optional[bool] = Field(
        False,
        is_flag=True,
        description="Return all runs using pagination (ignores limit).",
    )
    _api_version: str = PrivateAttr("v4")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs"

    def execute(self, pagination_token: str = None) -> requests.Response:
        if self.status is None:
            status = None
        else:
            status = self.status.value
        response = requests.get(
            url=self.api_url,
            headers={
                "x-dbt-continuation-token": pagination_token,
                **self.request_headers,
            },
            params={
                "limit": self.limit,
                "environment": self.environment_id,
                "project": self.project_id,
                "job": self.job_id,
                "status": status,
            },
        )
        return response
