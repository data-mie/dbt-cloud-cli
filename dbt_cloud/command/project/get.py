import requests
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import PROJECT_ID_FIELD


class DbtCloudProjectGetCommand(DbtCloudAccountCommand):
    """Retrieves dbt Cloud project information."""

    project_id: int = PROJECT_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects/{self.project_id}"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
