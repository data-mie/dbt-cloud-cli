from pydantic import BaseModel


class DbtCloudAPIv2(BaseModel):
    api_token: str
    api_base_url: str = "https://cloud.getdbt.com/api/v2"


class DbtCloudAccount(DbtCloudAPIv2):
    account_id: int

    def get_api_url(self) -> str:
        return f"{self.api_base_url}/accounts/{self.account_id}"
