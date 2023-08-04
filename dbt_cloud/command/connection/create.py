import requests
from typing import Optional, Union
from pydantic import Field, validator, BaseModel
from dbt_cloud.command.command import DbtCloudProjectCommand


class DbtCloudSnowflakeConnection(BaseModel):
    account: str = Field(description="Snowflake account name.")
    database: str = Field(description="Snowflake database name.")
    warehouse: str = Field(description="Snowflake warehouse name.")
    role: str = Field(description="Snowflake role name.")
    allow_sso: bool = Field(False, description="Allow SSO.")
    client_session_keep_alive: bool = Field(
        False, description="Keep client session alive."
    )


class DbtCloudConnectionCreateCommand(DbtCloudProjectCommand):
    """Creates a new database connection in a given project."""

    name: str = Field(description="Name of the connection.")
    type: str = Field(
        description="Type of the connection (e.g., 'snowflake'). Connection parameters go to the details field.",
    )
    id: Optional[int] = Field(description="ID of the connection.")
    created_by_id: Optional[int] = Field(
        description="ID of the user who created the connection."
    )
    created_by_service_token_id: Optional[int] = Field(
        description="ID of the service token that created the connection."
    )
    state: int = Field(1, description="State of the connection. 1 = Active.")

    details: Union[DbtCloudSnowflakeConnection, dict] = Field(
        description="Connection details specific to the connection type.",
        exclude_from_click_options=True,
    )

    @validator("type")
    def is_valid_type(cls, value):
        if value not in ["snowflake", "bigquery", "redshift", "postgres", "adapter"]:
            raise ValueError("Invalid connection type.")
        return value

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/connections/"

    def execute(self) -> requests.Response:
        response = requests.post(
            url=self.api_url, headers=self.request_headers, json=self.get_payload()
        )
        return response
