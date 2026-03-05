import json
import pytest
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.environment
@pytest.mark.integration
def test_cli_environment_list_and_get(runner, account_id, project_id):
    result = runner.invoke(
        cli,
        [
            "environment", "list",
            "--account-id", account_id,
            "--project-id", project_id,
            "--limit", 2,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for environment in response["data"]:
        assert environment["account_id"] == account_id

    environment_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        [
            "environment", "get",
            "--account-id", account_id,
            "--project-id", project_id,
            "--environment-id", environment_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == environment_id
    assert response["data"]["account_id"] == account_id
