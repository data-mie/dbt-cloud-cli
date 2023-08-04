import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.command.project.create import DbtCloudProjectCreateCommand


class DbtCloudProjectUpdateCommand(DbtCloudProjectCreateCommand):
    """Updates a project in a given account."""

    project_id: int = Field(description="ID of the project to update.")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/{self.project_id}"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json=self.get_payload(exclude_empty=True),
        )
        return response
