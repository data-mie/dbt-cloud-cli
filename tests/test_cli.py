import pytest
import json
from click.testing import CliRunner
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.integration
def test_cli_environment_get(account_id, environment_id):
    runner = CliRunner()
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


@pytest.mark.integration
def test_cli_environment_list(account_id):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["environment", "list", "--account-id", account_id, "--limit", 1],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert len(response["data"]) == 1
    for environment in response["data"]:
        assert environment["account_id"] == account_id


@pytest.mark.integration
def test_cli_project_create_and_delete(account_id):
    project_name = "pytest project"
    runner = CliRunner()

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


@pytest.mark.integration
def test_cli_connection_list_and_get(account_id, project_id):
    # Connection list
    runner = CliRunner()
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


@pytest.mark.integration
def test_cli_job_list_and_get(account_id, project_id):
    runner = CliRunner()

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


