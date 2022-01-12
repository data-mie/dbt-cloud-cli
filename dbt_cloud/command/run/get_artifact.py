import os
import requests
from typing import Optional, List
from pydantic import Field
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudRunGetArtifactCommand(DbtCloudCommand):
    """Fetches an artifact file from a completed run."""

    run_id: int = Field(
        ...,
        description="Numeric ID of the run",
    )
    step: int = Field(
        None,
        description="The index of the Step in the Run to query for artifacts. The first step in the run has the index 1. If the step parameter is omitted, then this endpoint will return the artifacts compiled for the last step in the run.",
    )
    path: str = Field(
        ...,
        description="Paths are rooted at the target/ directory. Use manifest.json, catalog.json, or run_results.json to download dbt-generated artifacts for the run.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs/{self.run_id}/artifacts/{self.path}"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url, headers=self.request_headers, params={"step": self.step}
        )
        return response
