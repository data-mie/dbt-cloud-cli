import json
import pytest
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.account
@pytest.mark.integration
def test_cli_account_list_and_get(runner):
    result = runner.invoke(cli, ["account", "list"])

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0

    account_id = response["data"][0]["id"]
    result = runner.invoke(cli, ["account", "get", "--account-id", account_id])

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == account_id
