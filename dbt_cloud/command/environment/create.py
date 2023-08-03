import requests
from typing import Optional
from pydantic import Field
from dbt_cloud.command.command import DbtCloudProjectCommand
from dbt_cloud.field import DBT_VERSION_FIELD


class DbtCloudEnvironmentCreateCommand(DbtCloudProjectCommand):
    """Creates a new dbt Cloud environment in a given project."""

    name: str = Field(
        description="Name of the environment.",
    )
    id: Optional[int]
    connection_id: Optional[int] = Field(
        description="Connection ID to use for this environment.",
    )
    credentials_id: Optional[int] = Field(
        description="Credentials ID to use for this environment.",
    )
    created_by_id: Optional[int] = Field(
        description="User ID of the user who created this environment.",
    )
    dbt_project_subdirectory: Optional[str] = Field(
        description="Subdirectory of the dbt project to use for this environment.",
    )
    use_custom_branch: bool = Field(
        False,
        description="Whether to use a custom branch for this environment.",
    )
    custom_branch: Optional[str] = Field(
        description="Custom branch to use for this environment.",
    )
    dbt_version: Optional[str] = DBT_VERSION_FIELD
    raw_dbt_version: Optional[str] = Field(
        description="Raw dbt version to use for this environment.",
    )
    supports_docs: bool = Field(
        False,
        description="Whether this environment supports docs.",
    )
    repository_id: Optional[int] = Field(
        description="Repository ID to use for this environment.",
    )
    state: int = Field(
        1,
        description="State of the environment. 1 = Active.",
    )
    custom_environment_variables: Optional[dict] = Field(
        description="Custom environment variables to use for this environment.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/environments"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json=self.get_payload(exclude_empty=True),
        )
        return response
