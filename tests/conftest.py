import json
import pytest
from pathlib import Path
from dbt_cloud.command import (
    DbtCloudJobCreateCommand,
    DbtCloudJobDeleteCommand,
    DbtCloudJobGetCommand,
    DbtCloudJobListCommand,
    DbtCloudJobRunCommand,
    DbtCloudProjectGetCommand,
    DbtCloudProjectListCommand,
    DbtCloudRunCancelCommand,
    DbtCloudRunGetArtifactCommand,
    DbtCloudRunGetCommand,
    DbtCloudRunListArtifactsCommand,
    DbtCloudRunListCommand,
    DbtCloudEnvironmentListCommand,
    DbtCloudAccountListCommand,
    DbtCloudAccountGetCommand,
    DbtCloudAuditLogGetCommand,
)


API_TOKEN = "foo"
ACCOUNT_ID = 123456
PROJECT_ID = 123457
ENVIRONMENT_ID = 49819
JOB_ID = 43167
RUN_ID = 36053848


def load_response(response_name):
    shared_datadir = Path(__file__).parent / "data"
    response_file = shared_datadir / f"{response_name}.json"
    response_json = response_file.read_text()
    return json.loads(response_json)


# A test case reads an example JSON response from tests/data and loads it to the request mocker (see mock_dbt_cloud_api fixture).
# A command.execute test then calls the API endpoint and verifies the response (the same example response that was loaded to the mocker).
# In other words, the test verifies that command.execute calls the correct endpoint with the correct HTTP method.
COMMAND_TEST_CASES = [
    pytest.param(
        "job_get",
        DbtCloudJobGetCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, job_id=JOB_ID
        ),
        load_response("job_get_response"),
        "get",
        marks=pytest.mark.job,
    ),
    pytest.param(
        "job_list",
        DbtCloudJobListCommand(api_token=API_TOKEN, account_id=ACCOUNT_ID),
        load_response("job_list_response"),
        "get",
        marks=pytest.mark.job,
    ),
    pytest.param(
        "job_create",
        DbtCloudJobCreateCommand(
            api_token=API_TOKEN,
            account_id=ACCOUNT_ID,
            project_id=PROJECT_ID,
            environment_id=ENVIRONMENT_ID,
            name="pytest job",
            execute_steps=["dbt seed", "dbt run", "dbt test"],
        ),
        load_response("job_create_response"),
        "post",
        marks=pytest.mark.job,
    ),
    pytest.param(
        "job_delete",
        DbtCloudJobDeleteCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, job_id=JOB_ID
        ),
        load_response("job_delete_response"),
        "delete",
        marks=pytest.mark.job,
    ),
    pytest.param(
        "job_run",
        DbtCloudJobRunCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, job_id=JOB_ID
        ),
        load_response("job_run_response"),
        "post",
        marks=pytest.mark.job,
    ),
    pytest.param(
        "run_cancel",
        DbtCloudRunCancelCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, run_id=RUN_ID
        ),
        load_response("run_cancel_response"),
        "post",
        marks=pytest.mark.run,
    ),
    pytest.param(
        "run_get",
        DbtCloudRunGetCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, run_id=RUN_ID
        ),
        load_response("run_get_response"),
        "get",
        marks=pytest.mark.run,
    ),
    pytest.param(
        "run_list",
        DbtCloudRunListCommand(api_token=API_TOKEN, account_id=ACCOUNT_ID),
        load_response("run_list_response"),
        "get",
        marks=pytest.mark.run,
    ),
    pytest.param(
        "run_list_artifacts",
        DbtCloudRunListArtifactsCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, run_id=RUN_ID
        ),
        load_response("run_list_artifacts_response"),
        "get",
        marks=pytest.mark.run,
    ),
    pytest.param(
        "run_get_artifact",
        DbtCloudRunGetArtifactCommand(
            api_token=API_TOKEN,
            account_id=ACCOUNT_ID,
            run_id=RUN_ID,
            path="run_results.json",
        ),
        load_response("run_get_artifact_response"),
        "get",
        marks=pytest.mark.run,
    ),
    pytest.param(
        "project_get",
        DbtCloudProjectGetCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, project_id=PROJECT_ID
        ),
        load_response("project_get_response"),
        "get",
        marks=pytest.mark.project,
    ),
    pytest.param(
        "project_list",
        DbtCloudProjectListCommand(api_token=API_TOKEN, account_id=ACCOUNT_ID),
        load_response("project_list_response"),
        "get",
        marks=pytest.mark.project,
    ),
    pytest.param(
        "environment_list",
        DbtCloudEnvironmentListCommand(
            api_token=API_TOKEN, account_id=ACCOUNT_ID, project_id=PROJECT_ID
        ),
        load_response("environment_list_response"),
        "get",
        marks=pytest.mark.environment,
    ),
    pytest.param(
        "account_list",
        DbtCloudAccountListCommand(api_token=API_TOKEN),
        load_response("account_list_response"),
        "get",
        marks=pytest.mark.account,
    ),
    pytest.param(
        "account_get",
        DbtCloudAccountGetCommand(api_token=API_TOKEN),
        load_response("account_get_response"),
        "get",
        marks=pytest.mark.account,
    ),
    pytest.param(
        "audit_log_get",
        DbtCloudAuditLogGetCommand(
            api_token=API_TOKEN,
            logged_at_start="2022-05-01",
            logged_at_end="2022-05-07",
        ),
        load_response("audit_log_get_response"),
        "get",
        marks=pytest.mark.audit_log,
    ),
]


@pytest.fixture
def mock_dbt_cloud_api(requests_mock):
    """Loads static JSON responses to a request mocker. Dynamic response mocking based on request has not been implemented yet."""
    for param in COMMAND_TEST_CASES:
        test_case_name, command, response, http_method = param.values
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


@pytest.fixture
def job_get():
    yield COMMAND_TEST_CASES[0]
