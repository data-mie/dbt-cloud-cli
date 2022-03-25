import os
import click
import ast
from pydantic import Field


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)


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
PROJECT_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_PROJECT_ID"],
    description="Numeric ID of a dbt Cloud project (default: DBT_CLOUD_PROJECT_ID environment variable)",
)
ENVIRONMENT_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_ENVIRONMENT_ID"],
    description="Numeric ID of a dbt Cloud environment (default: DBT_CLOUD_ENVIRONMENT_ID environment variable)",
)
JOB_ID_FIELD = Field(
    default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
    description="Numeric ID of a dbt Cloud job (default: DBT_CLOUD_JOB_ID environment variable)",
)
RUN_ID_FIELD = Field(
    ...,
    description="Numeric ID of a dbt Cloud run",
)
