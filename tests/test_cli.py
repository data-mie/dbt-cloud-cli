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
def test_cli_project_create(account_id):
    project_name = "pytest project"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "create", "--account-id", account_id, "--name", project_name],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert response["data"]["name"] == project_name
    assert response["data"]["account_id"] == account_id


@pytest.mark.integration
def test_cli_environment_create(account_id):
    environment_name = "pytest environment"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "environment",
            "create",
            "--account-id",
            account_id,
            "--name",
            environment_name,
            "--dbt-version",
            "1.4.0-latest",
        ],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert response["data"]["name"] == environment_name
    assert response["data"]["account_id"] == account_id
