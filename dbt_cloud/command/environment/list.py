import requests
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import PROJECT_ID_FIELD


class DbtCloudEnvironmentListCommand(DbtCloudAccountCommand):
    """Retrieves environments for a given project."""

    project_id: int = PROJECT_ID_FIELD
    _api_version: str = PrivateAttr("v3")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects/{self.project_id}/environments"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
