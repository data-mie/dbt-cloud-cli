import requests
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudAccountListCommand(DbtCloudCommand):
    """Retrieves all available accounts."""

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/accounts/"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
