import json
import pytest
from dbt_cloud import DbtCloudJob, DbtCloudRun
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
def job_get_response(shared_datadir):
    return load_response(shared_datadir, "job_get_response")


@pytest.fixture
def job_create_response(shared_datadir):
    return load_response(shared_datadir, "job_create_response")


@pytest.fixture
def job_delete_response(shared_datadir):
    return load_response(shared_datadir, "job_delete_response")


@pytest.fixture
def job_run_response(shared_datadir):
    return load_response(shared_datadir, "job_run_response")


@pytest.fixture
def run_get_response(shared_datadir):
    return load_response(shared_datadir, "run_get_response")


@pytest.fixture
def run_list_artifacts_response(shared_datadir):
    return load_response(shared_datadir, "run_list_artifacts_response")


@pytest.fixture
def run_get_artifact_response(shared_datadir):
    return load_response(shared_datadir, "run_get_artifact_response")


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
def job_get_command(api_token, account_id, job_id):
    command = DbtCloudJobGetCommand(
        api_token=api_token, account_id=account_id, job_id=job_id
    )
    yield command


@pytest.fixture
def job_create_command(api_token, account_id, project_id, environment_id):
    command = DbtCloudJobCreateCommand(
        api_token=api_token,
        account_id=account_id,
        project_id=project_id,
        environment_id=environment_id,
        name="pytest job",
        execute_steps=["dbt seed", "dbt run", "dbt test"],
    )
    yield command


@pytest.fixture
def job_delete_command(api_token, account_id, job_id):
    command = DbtCloudJobDeleteCommand(
        api_token=api_token, account_id=account_id, job_id=job_id
    )
    yield command


@pytest.fixture
def job_run_command(api_token, account_id, project_id, environment_id):
    command = DbtCloudJobRunCommand()
    yield command


@pytest.fixture
def run_get_command(api_token, account_id, run_id):
    command = DbtCloudRunGetCommand(
        api_token=api_token, account_id=account_id, run_id=run_id
    )
    yield command


@pytest.fixture
def run_list_artifacts_command(api_token, account_id, run_id):
    command = DbtCloudRunListArtifactsCommand(
        api_token=api_token, account_id=account_id, run_id=run_id
    )
    yield command


@pytest.fixture
def run_get_artifact_command(api_token, account_id, run_id):
    command = DbtCloudRunGetArtifactCommand(
        api_token=api_token,
        account_id=account_id,
        run_id=run_id,
        path="run_results.json",
    )
    yield command


""" OLD BELOW """


@pytest.fixture
def job(api_token, job_id, account_id):
    return DbtCloudJob(api_token=api_token, account_id=account_id, job_id=job_id)


@pytest.fixture
def run(job):
    return DbtCloudRun(run_id=36053848, **job.dict())


@pytest.fixture
def mock_dbt_cloud_api(
    requests_mock,
    job_get_command,
    job_get_response,
    job_create_command,
    job_create_response,
    job_delete_command,
    job_delete_response,
    job_run_command,
    job_run_response,
    run_get_command,
    run_get_response,
    run_list_artifacts_command,
    run_list_artifacts_response,
    run_get_artifact_command,
    run_get_artifact_response,
):
    requests_mock.get(
        job_get_command.api_url,
        json=job_get_response,
        status_code=job_get_response["status"]["code"],
    )

    requests_mock.post(
        job_create_command.api_url,
        json=job_create_response,
        status_code=job_create_response["status"]["code"],
    )

    requests_mock.delete(
        job_delete_command.api_url,
        json=job_delete_response,
        status_code=job_delete_response["status"]["code"],
    )

    requests_mock.post(
        job_run_command.api_url,
        json=job_run_response,
        status_code=job_run_response["status"]["code"],
    )

    requests_mock.get(
        run_get_command.api_url,
        json=run_get_response,
        status_code=run_get_response["status"]["code"],
    )

    requests_mock.get(
        run_list_artifacts_command.api_url,
        json=run_list_artifacts_response,
        status_code=run_list_artifacts_response["status"]["code"],
    )

    # Get artifact response include a status code
    requests_mock.get(
        run_get_artifact_command.api_url,
        json=run_get_artifact_response,
        status_code=200,
    )
