import os
from pydantic import Field

API_TOKEN_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
    description="API authentication key (default: 'DBT_CLOUD_API_TOKEN' environment variable)",
)
ACCOUNT_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
    description="Numeric ID of the Account that the job belongs to (default: 'DBT_CLOUD_ACCOUNT_ID' environment variable)",
)
JOB_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
    description="Numeric ID of the job to run (default: 'DBT_CLOUD_JOB_ID' environment variable)",
)
RUN_ID_FIELD = Field(
    ...,
    description="Numeric ID of the run",
)
