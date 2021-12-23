import json
import pytest
from dbt_cloud import DbtCloudJob, DbtCloudRun


def load_response(shared_datadir, response_name):
    response_file = shared_datadir / f"{response_name}.json"
    response_json = response_file.read_text()
    return json.loads(response_json)


@pytest.fixture
def job_get_response(shared_datadir):
    return load_response(shared_datadir, "job_get_response")


@pytest.fixture
def job_create_response(shared_datadir):
    return load_response(shared_datadir, "job_create_response")


@pytest.fixture
def job_run_response(shared_datadir):
    return load_response(shared_datadir, "job_run_response")


@pytest.fixture
def run_get_response(shared_datadir):
    return load_response(shared_datadir, "run_get_response")


@pytest.fixture
def project_id():
    return 123457


@pytest.fixture
def environment_id():
    return 49819


@pytest.fixture
def job():
    return DbtCloudJob(api_token="foo", account_id=123456, job_id=43167)


@pytest.fixture
def run(job):
    return DbtCloudRun(run_id=36053848, **job.dict())
