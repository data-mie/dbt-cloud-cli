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


class DbtCloudRunArgs(DbtCloudArgsBaseModel):
    run_id: int = Field(
        ...,
        description="Numeric ID of the run",
    )

    def get_run(self) -> "DbtCloudRun":
        return DbtCloudRun(
            run_id=self.run_id, api_token=self.api_token, account_id=self.account_id
        )


class DbtCloudRunGetArgs(DbtCloudRunArgs):
    include_related: Optional[List[str]] = Field(
        description="List of related fields to pull with the run. Valid values are 'trigger', 'job', and 'debug_logs'. If 'debug_logs' is not provided in a request, then the included debug logs will be truncated to the last 1,000 lines of the debug log output file.",
    )


class DbtCloudRunListArtifactsArgs(DbtCloudRunArgs):
    step: int = Field(
        None,
        description="The index of the Step in the Run to query for artifacts. The first step in the run has the index 1. If the step parameter is omitted, then this endpoint will return the artifacts compiled for the last step in the run.",
    )


class DbtCloudRunGetArtifactArgs(DbtCloudRunListArtifactsArgs):
    path: str = Field(
        ...,
        description="Paths are rooted at the target/ directory. Use manifest.json, catalog.json, or run_results.json to download dbt-generated artifacts for the run.",
    )


class DbtCloudRun(DbtCloudAccount):
    run_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.run_id}"

    def get_status(self) -> Tuple[requests.Response, DbtCloudRunStatus]:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers=self.authorization_headers,
        )
        return response, DbtCloudRunStatus(response.json()["data"]["status"])

    def list_artifacts(self, step: int = None) -> requests.Response:
        response = requests.get(
            url=f"{self.get_api_url()}/artifacts/",
            headers=self.authorization_headers,
            params={"step": step},
        )
        return response

    def get_artifact(self, path: str, step: int = None) -> requests.Response:
        response = requests.get(
            url=f"{self.get_api_url()}/artifacts/{path}",
            headers=self.authorization_headers,
            params={"step": step},
        )
        return response
