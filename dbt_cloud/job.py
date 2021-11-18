import requests
from enum import IntEnum
from typing import Optional
from dbt_cloud.account import DbtCloudAccount


class DbtCloudJobRunStatus(IntEnum):
    QUEUED = 1
    STARTING = 2
    RUNNING = 3
    SUCCESS = 10
    ERROR = 20
    CANCELLED = 30


class DbtCloudJob(DbtCloudAccount):
    job_id: int

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/jobs/{self.job_id}"

    def run(self, cause: str, git_sha: str) -> "DbtCloudJobRun":
        """
        :returns: Job run ID
        """
        payload = {"cause": cause}
        if git_sha:
            payload["git_sha"] = git_sha

        response = requests.post(
            url=f"{self.get_api_url()}/run/",
            headers={"Authorization": f"Token {self.api_token}"},
            json=payload,
        )
        response.raise_for_status()

        response_payload = response.json()
        job_run_id = response_payload["data"]["id"]
        return DbtCloudJobRun(
            job_run_id=job_run_id,
            payload=payload,
            account_id=self.account_id,
            api_token=self.api_token,
        )


class DbtCloudJobRun(DbtCloudAccount):
    job_run_id: int
    payload: Optional[dict]

    def get_api_url(self) -> str:
        return f"{super().get_api_url()}/runs/{self.job_run_id}"

    def get_status(self) -> DbtCloudJobRunStatus:
        response = requests.get(
            url=f"{self.get_api_url()}/",
            headers={"Authorization": f"Token {self.api_token}"},
        )
        response.raise_for_status()
        response_payload = response.json()
        return DbtCloudJobRunStatus(response_payload["data"]["status"])
