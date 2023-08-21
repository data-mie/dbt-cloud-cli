import requests
from pydantic import Field
from dbt_cloud.command.environment.create import DbtCloudEnvironmentCreateCommand


class DbtCloudEnvironmentUpdateCommand(DbtCloudEnvironmentCreateCommand):
    """Updates an environment in a given project."""

    environment_id: int = Field(description="ID of the environment to update.")

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/{self.environment_id}"

    def execute(self) -> requests.Response:
        payload = self.get_payload(exclude_empty=True)
        # Rename environment_id to id
        payload["id"] = payload.pop("environment_id")
        response = requests.post(
            url=self.api_url, headers=self.request_headers, json=payload
        )
        return response
