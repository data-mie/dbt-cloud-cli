import requests
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudProjectListCommand(DbtCloudAccountCommand):
    """Returns a list of projects in the account."""

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
