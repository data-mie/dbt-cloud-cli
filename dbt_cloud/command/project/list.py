import requests
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudProjectListCommand(DbtCloudCommand):
    """Returns a list of projects in the account."""
    _api_version: str = PrivateAttr("v3")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
