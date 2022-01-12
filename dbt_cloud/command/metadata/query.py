import requests
from pydantic import PrivateAttr
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudMetadataQueryCommand(DbtCloudCommand):
    """Queries the dbt Cloud Metadata API using GraphQL."""

    _query: str = PrivateAttr()

    @property
    def request_headers(self):
        return {"Authorization": f"Bearer {self.api_token}"}

    @property
    def api_url(self) -> str:
        return "https://metadata.cloud.getdbt.com/graphql"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url, headers=self.request_headers, data={"query": self._query}
        )
        return response
