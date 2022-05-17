import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudMetadataQueryCommand(DbtCloudAccountCommand):
    """Queries the dbt Cloud Metadata API using GraphQL."""

    query: str = Field(exclude_from_click_options=True)

    @property
    def request_headers(self):
        return {"Authorization": f"Bearer {self.api_token}"}

    @property
    def api_url(self) -> str:
        return f"https://metadata.{self.dbt_cloud_host}/graphql"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url, headers=self.request_headers, json={"query": self.query}
        )
        return response
