import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudProjectCommand


class DbtCloudConnectionGetCommand(DbtCloudProjectCommand):
    """Retrievies the details of a dbt Cloud database connection."""

    connection_id: int = Field(description="ID of the connection.")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/connections/{self.connection_id}/"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
