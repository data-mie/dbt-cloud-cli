import requests
from dbt_cloud.command import DbtCloudCommand


class DbtCloudMetadataAPI(DbtCloudCommand):
    """Queries the dbt Cloud Metadata API using GraphQL."""

    @property
    def request_headers(self):
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_api_url(self) -> str:
        return "https://metadata.cloud.getdbt.com/graphql"

    def query(self, query: str) -> requests.Response:
        response = requests.post(
            url=self.get_api_url(), headers=self.request_headers, data={"query": query}
        )
        return response
