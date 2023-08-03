import requests
from dbt_cloud.command.command import DbtCloudProjectCommand
from dbt_cloud.field import ACCOUNT_ID_FIELD, ENVIRONMENT_ID_FIELD


class DbtCloudEnvironmentGetCommand(DbtCloudProjectCommand):
    """Retrieves information about an environment in a given project."""

    environment_id: int = ENVIRONMENT_ID_FIELD
    account_id: int = ACCOUNT_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/environments/{self.environment_id}/"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
