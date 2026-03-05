import json
from dbt_cloud.cli import dbt_cloud as cli


def test_cli_run_list_and_get(runner, account_id, job_id):
    result = runner.invoke(
        cli,
        [
            "run", "list",
            "--account-id", account_id,
            "--job-id", job_id,
            "--paginate",
            "--status", "Succeeded",
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for run in response["data"]:
        assert run["account_id"] == account_id
        assert run["job_id"] == job_id

    run_id = response["data"][0]["id"]
    result = runner.invoke(
        cli, ["run", "get", "--account-id", account_id, "--run-id", run_id]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == run_id

    # Run get with include_related
    result = runner.invoke(
        cli,
        [
            "run", "get",
            "--account-id", account_id,
            "--run-id", run_id,
            "--include-related", "run_steps",
            "--include-related", "job",
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == run_id
    assert isinstance(response["data"]["run_steps"], list)
    assert response["data"]["job"] is not None


def test_cli_run_cancel_all(runner, account_id, job_id):
    for status in ("Queued", "Running"):
        result = runner.invoke(
            cli,
            [
                "run", "cancel-all",
                "--account-id", account_id,
                "--job-id", job_id,
                "--status", status,
                "-y",
            ],
        )
        assert result.exit_code == 0, result.output


def test_cli_run_list_and_get_artifacts(runner, account_id, job_id):
    result = runner.invoke(
        cli,
        [
            "run", "list",
            "--account-id", account_id,
            "--job-id", job_id,
            "--status", "Succeeded",
            "--limit", 1,
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    run_id = response["data"][0]["id"]

    result = runner.invoke(
        cli,
        ["run", "list-artifacts", "--account-id", account_id, "--run-id", run_id],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert len(response["data"]) > 0
    for artifact_path in response["data"]:
        assert isinstance(artifact_path, str)
        assert artifact_path != ""

    artifact_path = response["data"][0]
    result = runner.invoke(
        cli,
        [
            "run", "get-artifact",
            "--account-id", account_id,
            "--run-id", run_id,
            "--path", artifact_path,
        ],
    )

    assert result.exit_code == 0, result.output
