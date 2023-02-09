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

    def as_number(self) -> int:
        mapping = {
            self.QUEUED: 1,
            self.STARTING: 2,
            self.RUNNING: 3,
            self.SUCCEEDED: 10,
            self.FAILED: 20,
            self.CANCELED: 30,
        }
        return mapping[self]


class DbtCloudRunListCommand(DbtCloudAccountCommand):
    """Returns a list of runs in the account. The runs are returned sorted by creation date, with the most recent run appearing first."""

    job_id: Optional[str] = Field(description="Filter runs by job ID.")
    project_id: Optional[str] = Field(description="Filter runs by project ID.")
    status: Optional[DbtCloudRunStatus] = Field(description="Filter by run status.")
    order_by: Optional[str] = Field(
        description="Field to order the result by. Use '-' to indicate reverse order."
    )
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Offset for the returned runs. Must be a positive integer.",
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        le=100,
        description="A limit on the number of objects to be returned, between 1 and 100.",
    )
    _api_version: str = PrivateAttr("v2")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs"

    def execute(self, pagination_token: str = None) -> requests.Response:
        if self.status is None:
            status = None
        else:
            status = self.status.as_number()
        response = requests.get(
            url=self.api_url,
            headers={
                "x-dbt-continuation-token": pagination_token,
                **self.request_headers,
            },
            params={
                "limit": self.limit,
                "project_id": self.project_id,
                "job_definition_id": self.job_id,
                "status": status,
                "order_by": self.order_by,
                "offset": self.offset,
            },
        )
        return response
