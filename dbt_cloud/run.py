import requests
from enum import IntEnum
from typing import Optional, List, Tuple
from pydantic import Field
from dbt_cloud.account import DbtCloudAccount
from dbt_cloud.args import DbtCloudArgsBaseModel


class DbtCloudRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudRunGetArgs(DbtCloudArgsBaseModel):
    run_id: int = Field(
        ...,
        description="Numeric ID of the run",
    )
    include_related: Optional[List[str]] = Field(
        description="List of related fields to pull with the run. Valid values are 'trigger', 'job', and 'debug_logs'. If 'debug_logs' is not provided in a request, then the included debug logs will be truncated to the last 1,000 lines of the debug log output file.",
    )

    def get_run(self) -> "DbtCloudRun":
        return DbtCloudRun(
            run_id=self.run_id, api_token=self.api_token, account_id=self.account_id
        )


class DbtCloudRun(DbtCloudAccount):
    run_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.run_id}"

    def get_status(self) -> Tuple[requests.Response, DbtCloudRunStatus]:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
        )
        return response, DbtCloudRunStatus(response.json()["data"]["status"])
