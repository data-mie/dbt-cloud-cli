import pytest
import json
from click.testing import CliRunner
from dbt_cloud.cli import dbt_cloud as cli


@pytest.mark.online
def test_cli_environment_get(environment_id):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["environment", "get"],
    )

    assert result.exit_code == 0
    response = json.loads(result.output)
    assert response["data"]["id"] == environment_id
