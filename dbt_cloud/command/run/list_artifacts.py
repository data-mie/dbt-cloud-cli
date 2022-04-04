import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import RUN_ID_FIELD


class DbtCloudRunListArtifactsCommand(DbtCloudAccountCommand):
    """Fetches a list of artifact files generated for a completed run."""

    run_id: int = RUN_ID_FIELD
    step: int = Field(
        None,
        description="The index of the Step in the Run to query for artifacts. The first step in the run has the index 1. If the step parameter is omitted, then this endpoint will return the artifacts compiled for the last step in the run.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs/{self.run_id}/artifacts"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
