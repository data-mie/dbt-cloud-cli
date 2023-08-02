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
