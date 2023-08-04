import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudProjectCommand


class DbtCloudConnectionDeleteCommand(DbtCloudProjectCommand):
    """Deletes a database connection in a given project."""

    connection_id: int = Field(
        description="ID of the dbt Cloud database connection to delete.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/connections/{self.connection_id}/"

    def execute(self) -> requests.Response:
        response = requests.delete(url=self.api_url, headers=self.request_headers)
        return response
