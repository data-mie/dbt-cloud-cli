import requests
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudAccountGetCommand(DbtCloudAccountCommand):
    """Retrieves dbt Cloud account information."""

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
