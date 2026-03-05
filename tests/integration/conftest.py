import json
import pytest
from click.testing import CliRunner
from dbt_cloud.cli import dbt_cloud as cli


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def dbt_cloud_project(runner, account_id):
    project_name = "pytest project"
    result = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--account-id",
            account_id,
            "--name",
            project_name,
            "--type",
            0,
        ],
    )
    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["name"] == project_name
    assert response["data"]["account_id"] == account_id

    yield response["data"]

    project_id = response["data"]["id"]
    result = runner.invoke(
        cli,
        ["project", "delete", "--account-id", account_id, "--project-id", project_id],
    )
    assert result.exit_code == 0, result.output


@pytest.fixture(scope="session")
def dbt_cloud_environment(dbt_cloud_project, runner, account_id):
    environment_name = "pytest environment"
    project_id = dbt_cloud_project["id"]
    result = runner.invoke(
        cli,
        [
            "environment",
            "create",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--name",
            environment_name,
            "--type",
            "deployment",
            "--dbt-version",
            "1.5.0-latest",
        ],
    )
    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    environment_id = response["data"]["id"]
    assert response["data"]["name"] == environment_name
    assert response["data"]["account_id"] == account_id
    assert response["data"]["type"] == "deployment"

    yield response["data"]

    result = runner.invoke(
        cli,
        [
            "environment",
            "delete",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--environment-id",
            environment_id,
        ],
    )
    assert result.exit_code == 0, result.output


@pytest.fixture(scope="session")
def dbt_cloud_job(runner, dbt_cloud_environment, account_id):
    project_id = dbt_cloud_environment["project_id"]
    environment_id = dbt_cloud_environment["id"]
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
            '["dbt compile"]',
        ],
    )
    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    job_id = response["data"]["id"]
    assert response["data"]["account_id"] == account_id
    assert response["data"]["project_id"] == project_id
    assert response["data"]["environment_id"] == environment_id
    assert response["data"]["settings"]["threads"] == 4

    yield response["data"]

    result = runner.invoke(
        cli,
        ["job", "delete", "--account-id", account_id, "--job-id", job_id],
    )
    assert result.exit_code == 0, result.output
