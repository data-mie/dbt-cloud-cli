import requests
from pydantic import PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import ACCOUNT_ID_FIELD, ENVIRONMENT_ID_FIELD


class DbtCloudEnvironmentGetCommand(DbtCloudAccountCommand):
    """Retrieves information about an environment in a given account."""

    environment_id: int = ENVIRONMENT_ID_FIELD
    account_id: int = ACCOUNT_ID_FIELD
    _api_version: str = PrivateAttr("v2")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/environments/{self.environment_id}/"

    def execute(self) -> requests.Response:
        response = requests.get(url=self.api_url, headers=self.request_headers)
        return response
