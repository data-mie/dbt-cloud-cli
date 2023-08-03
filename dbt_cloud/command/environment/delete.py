import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudProjectCommand


class DbtCloudEnvironmentDeleteCommand(DbtCloudProjectCommand):
    """Deletes a dbt Cloud environment in a given project."""

    environment_id: int = Field(
        description="ID of the dbt Cloud environment to delete.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/environments/{self.environment_id}/"

    def execute(self) -> requests.Response:
        response = requests.delete(url=self.api_url, headers=self.request_headers)
        return response
