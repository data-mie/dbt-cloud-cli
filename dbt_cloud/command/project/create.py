import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudProjectCreateCommand(DbtCloudAccountCommand):
    """Creates a new dbt Cloud project in a given account."""

    name: str = Field(description="Name of the project.")
    connection_id: Optional[int] = Field(description="ID of the connection to use.")
    repository_id: Optional[int] = Field(description="ID of the repository to use.")
    semantic_layer_config_id: Optional[int] = Field(
        description="ID of the semantic layer config to use."
    )
    skipped_setup: Optional[bool] = Field(description="Whether to skip setup.")
    state: int = Field(1, description="State of the project. 1 = Active.")
    dbt_project_subdirectory: Optional[str] = Field(
        description="Subdirectory of the dbt project to use."
    )
    docs_job_id: Optional[int] = Field(description="ID of the docs job to use.")
    freshness_job_id: Optional[int] = Field(
        description="ID of the freshness job to use."
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json=self.get_payload(exclude_empty=True),
        )
        return response
