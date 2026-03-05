import json
import pytest
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.project
@pytest.mark.integration
def test_cli_project_list_and_get(runner, account_id):
    result = runner.invoke(
        cli, ["project", "list", "--account-id", account_id, "--limit", 2]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for project in response["data"]:
        assert project["account_id"] == account_id

    project_id = response["data"][0]["id"]
    result = runner.invoke(
        cli, ["project", "get", "--account-id", account_id, "--project-id", project_id]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == project_id


@pytest.mark.project
@pytest.mark.integration
def test_cli_project_update(runner, account_id, dbt_cloud_project):
    project_id = dbt_cloud_project["id"]

    result = runner.invoke(
        cli,
        [
            "project", "update",
            "--account-id", account_id,
            "--project-id", project_id,
            "--name", "pytest project updated",
            "--type", dbt_cloud_project["type"],
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == project_id
    assert response["data"]["name"] == "pytest project updated"
