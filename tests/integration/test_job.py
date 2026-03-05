import json
import pytest
from dbt_cloud.cli import dbt_cloud as cli


def test_cli_job_list_and_get(runner, account_id, project_id):
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

    job_id = response["data"][0]["id"]
    result = runner.invoke(
        cli, ["job", "get", "--account-id", account_id, "--job-id", job_id]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == job_id

    # Job get with include_related
    result = runner.invoke(
        cli,
        [
            "job",
            "get",
            "--account-id",
            account_id,
            "--job-id",
            job_id,
            "--include-related",
            "environment",
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == job_id
    assert response["data"]["environment"] is not None


def test_cli_job_export_and_import(runner, account_id, dbt_cloud_job):
    job_id = dbt_cloud_job["id"]

    result = runner.invoke(
        cli, ["job", "export", "--account-id", account_id, "--job-id", job_id]
    )

    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["job", "import"], input=result.output)

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] != job_id
    imported_job_id = response["data"]["id"]

    result = runner.invoke(
        cli, ["job", "delete", "--account-id", account_id, "--job-id", imported_job_id]
    )

    assert result.exit_code == 0, result.output


def test_cli_job_delete_all(runner, account_id, dbt_cloud_job):
    project_id = dbt_cloud_job["project_id"]
    environment_id = dbt_cloud_job["environment_id"]
    job_ids_to_keep = [dbt_cloud_job["id"]]

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
            "--execute-steps",
            '["dbt seed"]',
        ],
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    job_id = response["data"]["id"]

    result = runner.invoke(
        cli,
        [
            "job",
            "delete-all",
            "--account-id",
            account_id,
            "--project-id",
            project_id,
            "--keep-jobs",
            str(job_ids_to_keep),
            "--yes",
        ],
    )

    assert result.exit_code == 0, result.output
    assert f"Jobs to delete: [{job_id}]" in result.output
    assert f"Job {job_id} was deleted" in result.output


def test_cli_job_run_wait(runner, job_id, account_id):
    result = runner.invoke(
        cli,
        ["job", "run", "--account-id", account_id, "--job-id", job_id, "--wait"],
    )

    assert result.exit_code == 0, result.output


def test_cli_job_run_no_wait_and_cancel(runner, account_id, job_id):
    result = runner.invoke(
        cli, ["job", "run", "--account-id", account_id, "--job-id", job_id]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    run_id = response["data"]["id"]

    result = runner.invoke(
        cli, ["run", "cancel", "--account-id", account_id, "--run-id", run_id]
    )

    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    assert response["data"]["id"] == run_id
