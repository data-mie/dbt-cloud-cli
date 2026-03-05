import json
import requests
from enum import IntEnum
from typing import Optional, List
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import RUN_ID_FIELD


class DbtCloudRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudRunGetCommand(DbtCloudAccountCommand):
    """Returns the details of a dbt Cloud run."""

    _api_version: str = PrivateAttr("v2")
    run_id: int = RUN_ID_FIELD
    include_related: Optional[List[str]] = Field(
        default=None,
        description="A list of related objects to include in the response. Valid values are trigger, job, environment, repository, run_steps, run_retries, used_repo_cache, repo_cache_restore, audit, and debug_logs. If debug_logs is not provided, then the included debug logs will be truncated to the last 1,000 lines of the debug log output file.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs/{self.run_id}"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={
                "include_related": (
                    json.dumps(list(self.include_related))
                    if self.include_related
                    else None
                )
            },
        )
        return response
