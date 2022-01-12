import os
import requests
from enum import IntEnum
from typing import Optional, List
from pydantic import Field
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudRunGetCommand(DbtCloudCommand):
    """Prints a dbt Cloud run status JSON response."""

    run_id: int = Field(
        ...,
        description="Numeric ID of the run",
    )
    include_related: Optional[List[str]] = Field(
        description="List of related fields to pull with the run. Valid values are 'trigger', 'job', and 'debug_logs'. If 'debug_logs' is not provided in a request, then the included debug logs will be truncated to the last 1,000 lines of the debug log output file.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs/{self.run_id}"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
