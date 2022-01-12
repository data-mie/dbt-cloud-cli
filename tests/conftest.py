import json
import pytest
from dbt_cloud.command import (
    DbtCloudJobGetCommand,
    DbtCloudJobCreateCommand,
    DbtCloudJobDeleteCommand,
    DbtCloudJobRunCommand,
    DbtCloudRunGetCommand,
    DbtCloudRunListArtifactsCommand,
    DbtCloudRunGetArtifactCommand,
)


def load_response(shared_datadir, response_name):
    response_file = shared_datadir / f"{response_name}.json"
    response_json = response_file.read_text()
    return json.loads(response_json)


@pytest.fixture
def job_delete_response(shared_datadir):
    return load_response(shared_datadir, "job_delete_response")


@pytest.fixture
def job_run_response(shared_datadir):
    return load_response(shared_datadir, "job_run_response")


@pytest.fixture
def api_token():
    return "foo"


@pytest.fixture
def account_id():
    return 123456


@pytest.fixture
def project_id():
    return 123457


@pytest.fixture
def environment_id():
    return 49819


@pytest.fixture
def job_id():
    return 43167


@pytest.fixture
def run_id():
    return 36053848


@pytest.fixture
def run_get(shared_datadir, api_token, account_id, run_id):
    command = DbtCloudRunGetCommand(
        api_token=api_token, account_id=account_id, run_id=run_id
    )
    response = load_response(shared_datadir, "run_get_response")
    http_method = "get"
    yield command, response, http_method


@pytest.fixture
def run_list_artifacts(shared_datadir, api_token, account_id, run_id):
    command = DbtCloudRunListArtifactsCommand(
        api_token=api_token, account_id=account_id, run_id=run_id
    )
    response = load_response(shared_datadir, "run_list_artifacts_response")
    http_method = "get"
    yield command, response, http_method


@pytest.fixture
def run_get_artifact(shared_datadir, api_token, account_id, run_id):
    command = DbtCloudRunGetArtifactCommand(
        api_token=api_token,
        account_id=account_id,
        run_id=run_id,
        path="run_results.json",
    )
    response = load_response(shared_datadir, "run_get_artifact_response")
    http_method = "get"
    yield command, response, http_method


@pytest.fixture
def job_get(shared_datadir, api_token, account_id, job_id):
    command = DbtCloudJobGetCommand(
        api_token=api_token, account_id=account_id, job_id=job_id
    )
    response = load_response(shared_datadir, "job_get_response")
    http_method = "get"
    yield command, response, http_method


@pytest.fixture
def job_create(shared_datadir, api_token, account_id, project_id, environment_id):
    command = DbtCloudJobCreateCommand(
        api_token=api_token,
        account_id=account_id,
        project_id=project_id,
        environment_id=environment_id,
        name="pytest job",
        execute_steps=["dbt seed", "dbt run", "dbt test"],
    )
    response = load_response(shared_datadir, "job_create_response")
    http_method = "post"
    yield command, response, http_method


@pytest.fixture
def job_delete(shared_datadir, api_token, account_id, job_id):
    command = DbtCloudJobDeleteCommand(
        api_token=api_token, account_id=account_id, job_id=job_id
    )
    response = load_response(shared_datadir, "job_delete_response")
    http_method = "delete"
    yield command, response, http_method


@pytest.fixture
def job_run(shared_datadir, api_token, account_id, job_id):
    command = DbtCloudJobRunCommand(
        api_token=api_token, account_id=account_id, job_id=job_id
    )
    response = load_response(shared_datadir, "job_run_response")
    http_method = "post"
    yield command, response, http_method


@pytest.fixture
def mock_dbt_cloud_api(
    requests_mock,
    job_get,
    job_create,
    job_delete,
    job_run,
    run_get,
    run_list_artifacts,
    run_get_artifact,
):
    command_fixtures = (
        job_get,
        job_create,
        job_delete,
        job_run,
        run_get,
        run_list_artifacts,
        run_get_artifact,
    )
    for command, response, http_method in command_fixtures:
        try:
            status_code = response["status"]["code"]
        except KeyError:
            # Get artifact response include a status code
            status_code = 200

        requests_mock_method = getattr(requests_mock, http_method)
        requests_mock_method(
            command.api_url,
            json=response,
            status_code=status_code,
        )
