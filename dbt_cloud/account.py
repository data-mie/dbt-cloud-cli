from pydantic import BaseModel


class DbtCloudAPI(BaseModel):
    api_token: str


class DbtCloudAccount(DbtCloudAPI):
    account_id: int

    def get_api_url(self, api_version: str = "v2") -> str:
        return f"https://cloud.getdbt.com/api/{api_version}/accounts/{self.account_id}"

    @property
    def authorization_headers(self):
        return {"Authorization": f"Token {self.api_token}"}
