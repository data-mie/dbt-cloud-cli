import requests
from typing import Optional, Literal, Union
from pydantic import Field, BaseModel
from dbt_cloud.command.command import DbtCloudAccountCommand


class DbtCloudSnowflakeConnection(BaseModel):
    type: str = Literal["snowflake"]
    account: str = Field(description="Snowflake account name.")
    database: str = Field(description="Snowflake database name.")
    warehouse: str = Field(description="Snowflake warehouse name.")
    allow_sso: bool = Field(description="Allow SSO.")


class DbtCloudBigQueryConnection(BaseModel):
    type: str = Literal["bigquery"]
    client_id: str = Field(description="BigQuery client ID.")
    project_id: str = Field(description="BigQuery project ID.")
    timeout_seconds: int = Field(description="BigQuery timeout in seconds.")
    client_x509_cert_url: str = Field(description="BigQuery client x509 cert URL.")
    private_key_id: str = Field(description="BigQuery private key ID.")
    token_uri: str = Field(description="BigQuery token URI.")
    auth_provider_x509_cert_url: str = Field(
        description="BigQuery auth provider x509 cert URL."
    )
    auth_uri: str = Field(description="BigQuery auth URI.")
    client_email: str = Field(description="BigQuery client email.")


class DbtCloudConnectionCreateCommand(DbtCloudAccountCommand):
    """Creates a new database connection in a given account."""

    name: str = Field(description="Name of the connection.")
    type: str = Field(
        description="Type of the connection (e.g., 'snowflake'). Connection parameters specific to the connection are input as separate arguments."
    )
    id: Optional[int] = Field(description="ID of the connection.")
    created_by_id: Optional[int] = Field(
        description="ID of the user who created the connection."
    )
    created_by_service_token_id: Optional[int] = Field(
        description="ID of the service token that created the connection."
    )
    state: int = Field(description="State of the connection. 1 = Active.")

    connection_parameters: Union[
        DbtCloudSnowflakeConnection, DbtCloudBigQueryConnection
    ] = Field(exclude_from_click_options=True)

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/connections/"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url,
            headers=self.request_headers,
            json={
                **self.get_payload(
                    exclude=[
                        "api_token",
                        "dbt_cloud_host",
                        "connection_parameters",
                        "type",
                    ]
                ),
                **self.connection_parameters.dict(),
            },
        )
        return response
