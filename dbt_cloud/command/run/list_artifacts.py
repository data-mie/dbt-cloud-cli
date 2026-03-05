import requests
from typing import Optional
from pydantic import Field, PrivateAttr
from dbt_cloud.command.command import DbtCloudAccountCommand
from dbt_cloud.field import RUN_ID_FIELD


class DbtCloudRunListArtifactsCommand(DbtCloudAccountCommand):
    """Fetches a list of artifact files generated for a completed run."""

    _api_version: str = PrivateAttr("v2")
    run_id: int = RUN_ID_FIELD
    include_related: Optional[str] = Field(
        default=None,
        description="Comma-separated list of related objects to include in the response.",
    )

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/runs/{self.run_id}/artifacts"

    def execute(self) -> requests.Response:
        response = requests.get(
            url=self.api_url,
            headers=self.request_headers,
            params={"include_related": self.include_related},
        )
        return response
