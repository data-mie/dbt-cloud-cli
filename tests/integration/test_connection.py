import json
import pytest
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.connection
@pytest.mark.integration
@pytest.mark.parametrize(
    "connection_type,args",
    [
        (
            "snowflake",
            [
                "--account", "snowflake_account",
                "--database", "snowflake_database",
                "--warehouse", "snowflake_warehouse",
                "--role", "snowflake_role",
                "--allow-sso", "False",
                "--client-session-keep-alive", "False",
            ],
        ),
    ],
)
def test_cli_connection_create_and_delete(
    runner, account_id, dbt_cloud_project, connection_type, args
):
    project_id = dbt_cloud_project["id"]
    connection_name = "pytest connection"

    result = runner.invoke(
        cli,
        [
            "connection", "create",
            "--account-id", account_id,
            "--project-id", project_id,
            "--name", connection_name,
            "--type", connection_type,
        ] + args,
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["name"] == connection_name
    assert response["data"]["account_id"] == account_id

    connection_id = response["data"]["id"]
    result = runner.invoke(
        cli,
        [
            "connection", "delete",
            "--account-id", account_id,
            "--project-id", project_id,
            "--connection-id", connection_id,
        ],
    )

    assert result.exit_code == 0, result.output


@pytest.mark.connection
@pytest.mark.integration
def test_cli_connection_list_and_get(runner, account_id, project_id):
    result = runner.invoke(
        cli,
        [
            "connection", "list",
            "--account-id", account_id,
            "--project-id", project_id,
            "--limit", 2,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for connection in response["data"]:
        assert connection["account_id"] == account_id

    connection_id = response["data"][0]["id"]
    result = runner.invoke(
        cli,
        [
            "connection", "get",
            "--account-id", account_id,
            "--connection-id", connection_id,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == connection_id
