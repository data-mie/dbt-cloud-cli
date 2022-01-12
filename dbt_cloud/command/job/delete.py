import os
import requests
from pydantic import Field
from dbt_cloud.command.command import DbtCloudCommand


class DbtCloudJobDeleteCommand(DbtCloudCommand):
    """Deletes a job from a dbt Cloud project."""

    job_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_JOB_ID"],
        description="Numeric ID of the job to run (default: 'DBT_CLOUD_JOB_ID' environment variable)",
    )

    @property
    def api_url(self) -> str:
        api_url = f"{super().api_url}/jobs"
        if self.job_id is not None:
            api_url = f"{api_url}/{self.job_id}"
        return api_url

    def execute(self) -> requests.Response:
        response = requests.delete(url=self.api_url, headers=self.request_headers)
        return response
