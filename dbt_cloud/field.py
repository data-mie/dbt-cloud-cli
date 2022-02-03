import os
from pydantic import Field

DBT_CLOUD_HOST_FIELD = Field(
    default_factory=lambda: os.getenv("DBT_CLOUD_HOST", default="cloud.getdbt.com"),
    description="dbt Cloud Host (defaults to 'cloud.getdbt.com' unless DBT_CLOUD_HOST environment variable is set)",
)

API_TOKEN_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
    description="API authentication key (default: DBT_CLOUD_API_TOKEN environment variable)",
)
ACCOUNT_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
    description="Numeric ID of the dbt Cloud account (default: DBT_CLOUD_ACCOUNT_ID environment variable)",
)
JOB_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
    description="Numeric ID of a dbt Cloud job (default: DBT_CLOUD_JOB_ID environment variable)",
)
RUN_ID_FIELD = Field(
    ...,
    description="Numeric ID of a dbt Cloud run",
)
