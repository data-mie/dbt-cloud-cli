import os
from pydantic import Field
from dbt_cloud.args import ArgsBaseModel


class DbtCloudAPI(ArgsBaseModel):
    api_token: str = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
        description="API authentication key (default: 'DBT_CLOUD_API_TOKEN' environment variable)",
    )


class DbtCloudAccount(DbtCloudAPI):
    account_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
        description="Numeric ID of the Account that the job belongs to (default: 'DBT_CLOUD_ACCOUNT_ID' environment variable)",
    )

    def get_api_url(self, api_version: str = "v2") -> str:
        return f"https://cloud.getdbt.com/api/{api_version}/accounts/{self.account_id}"

    @property
    def request_headers(self):
        return {"Authorization": f"Token {self.api_token}"}
