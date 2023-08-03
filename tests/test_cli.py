import pytest
import json
from click.testing import CliRunner
from dbt_cloud.cli import dbt_cloud as cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.account
@pytest.mark.integration
def test_cli_account_list_and_get(runner):
    # Account list
    result = runner.invoke(
        cli,
        ["account", "list"],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert len(response["data"]) > 0

    # Account get
    account_id = response["data"][0]["id"]
    print(account_id)
    result = runner.invoke(
        cli,
        ["account", "get", "--account-id", account_id],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert response["data"]["id"] == account_id


@pytest.mark.environment
@pytest.mark.integration
def test_cli_environment_list_and_get(runner, account_id):
    # Environment list
    result = runner.invoke(
        cli,
        ["environment", "list", "--account-id", account_id, "--limit", 2],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    environment_id = response["data"][0]["id"]
    assert len(response["data"]) > 0
    for environment in response["data"]:
        assert environment["account_id"] == account_id

    result = runner.invoke(
        cli,
        [
            "environment",
            "get",
            "--account-id",
            account_id,
            "--environment-id",
            environment_id,
        ],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert response["data"]["id"] == environment_id
    assert response["data"]["account_id"] == account_id


@pytest.mark.project
@pytest.mark.integration
def test_cli_project_list_and_get(runner, account_id):
    # Project list
    result = runner.invoke(
        cli,
        ["project", "list", "--account-id", account_id, "--limit", 2],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for project in response["data"]:
        assert project["account_id"] == account_id

    # Project get
    project_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        ["project", "get", "--account-id", account_id, "--project-id", project_id],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == project_id


@pytest.mark.project
@pytest.mark.integration
def test_cli_project_create_and_delete(runner, account_id):
    project_name = "pytest project"

    # Project create
    result = runner.invoke(
        cli,
        ["project", "create", "--account-id", account_id, "--name", project_name],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["name"] == project_name
    assert response["data"]["account_id"] == account_id

    # Project delete
    project_id = response["data"]["id"]
    result = runner.invoke(
        cli,
        ["project", "delete", "--account-id", account_id, "--project-id", project_id],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == project_id
    assert response["data"]["account_id"] == account_id


@pytest.mark.connection
@pytest.mark.integration
def test_cli_connection_list_and_get(runner, account_id, project_id):
    # Connection list
    result = runner.invoke(
        cli,
        [
            "connection",
            "list",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--limit",
            2,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for connection in response["data"]:
        assert connection["account_id"] == account_id

    # Connection get
    connection_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        [
            "connection",
            "get",
            "--account-id",
            account_id,
            "--connection-id",
            connection_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == connection_id


@pytest.mark.job
@pytest.mark.integration
def test_cli_job_list_and_get(runner, account_id, project_id):
    # Job list
    result = runner.invoke(
        cli,
        [
            "job",
            "list",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--limit",
            2,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for job in response["data"]:
        assert job["account_id"] == account_id
        assert job["project_id"] == project_id

    # Job get
    job_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        [
            "job",
            "get",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == job_id


@pytest.mark.job
@pytest.mark.integration
def test_cli_job_create_and_delete(runner, account_id, project_id, environment_id):
    # Job create
    result = runner.invoke(
        cli,
        [
            "job",
            "create",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--environment-id",
            environment_id,
            "--name",
            "pytest job",
            "--settings-threads",
            4,
            "--execute-steps",
            '["dbt seed"]',
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    job_id = response["data"]["id"]
    assert response["data"]["account_id"] == account_id
    assert response["data"]["project_id"] == project_id
    assert response["data"]["environment_id"] == environment_id
    assert response["data"]["settings"]["threads"] == 4

    # Job delete
    result = runner.invoke(
        cli,
        [
            "job",
            "delete",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == job_id


@pytest.mark.job
@pytest.mark.integration
def test_cli_job_export_and_import(runner, account_id, job_id):
    # Job export
    result = runner.invoke(
        cli,
        [
            "job",
            "export",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)

    # Job import
    result = runner.invoke(
        cli,
        [
            "job",
            "import",
        ],
        input=result.output,
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] != job_id
    job_id = response["data"]["id"]

    # Job delete
    result = runner.invoke(
        cli,
        [
            "job",
            "delete",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == job_id


@pytest.mark.job
@pytest.mark.integration
def test_cli_job_run_wait(runner, account_id, job_id):
    result = runner.invoke(
        cli,
        ["job", "run", "--account-id", account_id, "--job-id", job_id, "--wait"],
    )

    assert result.exit_code == 0, result.output


@pytest.mark.job
@pytest.mark.integration
def test_cli_job_run_no_wait_and_cancel(runner, account_id, job_id):
    result = runner.invoke(
        cli,
        ["job", "run", "--account-id", account_id, "--job-id", job_id],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    run_id = response["data"]["id"]

    result = runner.invoke(
        cli,
        [
            "run",
            "cancel",
            "--account-id",
            account_id,
            "--run-id",
            run_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == run_id


@pytest.mark.run
@pytest.mark.integration
def test_cli_run_list_and_get(runner, account_id, job_id):
    # Run list
    result = runner.invoke(
        cli,
        [
            "run",
            "list",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
            "--paginate",
            "--status",
            "Succeeded",
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for run in response["data"]:
        assert run["account_id"] == account_id
        assert run["job_id"] == job_id

    # Run get
    run_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        [
            "run",
            "get",
            "--account-id",
            account_id,
            "--run-id",
            run_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == run_id


@pytest.mark.run
@pytest.mark.integration
def test_cli_run_cancel_all(runner, account_id, job_id):
    # Run cancel all queued
    result = runner.invoke(
        cli,
        [
            "run",
            "cancel-all",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
            "--status",
            "Queued",
            "-y",
        ],
    )

    assert result.exit_code == 0, result.output

    # Run cancel all running
    result = runner.invoke(
        cli,
        [
            "run",
            "cancel-all",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
            "--status",
            "Running",
            "-y",
        ],
    )

    assert result.exit_code == 0, result.output


@pytest.mark.run
@pytest.mark.integration
def test_cli_run_list_and_get_artifacts(runner, account_id, job_id):
    # Run list
    result = runner.invoke(
        cli,
        [
            "run",
            "list",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
            "--status",
            "Succeeded",
            "--limit",
            1,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    run_id = response["data"][0]["id"]

    # Run list artifacts
    result = runner.invoke(
        cli,
        [
            "run",
            "list-artifacts",
            "--account-id",
            account_id,
            "--run-id",
            run_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for artifact_path in response["data"]:
        assert isinstance(artifact_path, str)
        assert artifact_path != ""

    # Run get artifact
    artifact_path = response["data"][0]
    result = runner.invoke(
        cli,
        [
            "run",
            "get-artifact",
            "--account-id",
            account_id,
            "--run-id",
            run_id,
            "--path",
            artifact_path,
        ],
    )

    assert result.exit_code == 0, result.output
