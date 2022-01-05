import requests
from enum import IntEnum
from typing import Optional, List, Tuple
from pydantic import Field
from dbt_cloud.account import DbtCloudAccount
from dbt_cloud.args import DbtCloudArgsBaseModel


class DbtCloudMetadataAPI(DbtCloudAccount):
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
