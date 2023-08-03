import requests
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudProjectDeleteCommand(DbtCloudAccountCommand):
    """Deletes a dbt Cloud project in a given account."""

    _api_version: str = PrivateAttr("v3")
    project_id: int = Field(
        description="ID of the dbt Cloud project to delete.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects/{self.project_id}/"

    def execute(self) -> requests.Response:
        response = requests.delete(url=self.api_url, headers=self.request_headers)
        return response
