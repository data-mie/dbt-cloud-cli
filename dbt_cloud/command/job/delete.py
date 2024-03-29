import requests
from pydantic import PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import JOB_ID_FIELD


class DbtCloudJobDeleteCommand(DbtCloudAccountCommand):
    """Deletes a job from a dbt Cloud project."""

    _api_version: str = PrivateAttr("v2")
    job_id: int = JOB_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/jobs/{self.job_id}"

    def execute(self) -> requests.Response:
        response = requests.delete(url=self.api_url, headers=self.request_headers)
        return response
