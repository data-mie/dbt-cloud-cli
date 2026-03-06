"""Tests for CLI-level behaviour: output routing, error handling, exit codes."""

import json
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
from requests import HTTPError
from requests.models import Response
from dbt_cloud.cli import dbt_cloud as cli


@pytest.fixture
def runner():
    return CliRunner()


def _mock_response(status_code, body):
    """Build a mock requests.Response with the given status and JSON body."""
    resp = MagicMock(spec=Response)
    resp.status_code = status_code
    resp.json.return_value = body
    if status_code >= 400:
        http_error = HTTPError(f"{status_code} Client Error")
        http_error.response = resp
        resp.raise_for_status.side_effect = http_error
    else:
        resp.raise_for_status.return_value = None
    return resp


def _extract_json(output):
    """Parse the first complete JSON object from mixed output."""
    decoder = json.JSONDecoder()
    idx = output.find("{")
    assert idx != -1, f"No JSON found in output: {output!r}"
    obj, _ = decoder.raw_decode(output, idx)
    return obj


SUCCESS_BODY = {
    "status": {"code": 200, "is_success": True},
    "data": {"id": 42},
}

ERROR_BODY = {
    "status": {"code": 401, "is_success": False, "user_message": "Unauthorized"},
    "data": {},
}


class TestHttpErrorHandling:
    def test_exit_code_0_on_success(self, runner):
        mock_resp = _mock_response(200, SUCCESS_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        assert result.exit_code == 0

    def test_exit_code_1_on_http_error(self, runner):
        mock_resp = _mock_response(401, ERROR_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        assert result.exit_code == 1

    def test_json_body_present_on_error(self, runner):
        mock_resp = _mock_response(401, ERROR_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        assert result.exit_code == 1
        assert _extract_json(result.output) == ERROR_BODY

    def test_no_traceback_on_http_error(self, runner):
        mock_resp = _mock_response(500, ERROR_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        assert result.exit_code == 1
        assert "Traceback" not in result.output


class TestStatusMessagesRouteToStderr:
    """Verify that human-readable status messages use err=True (→ stderr)."""

    def test_error_message_uses_err_true(self, runner):
        mock_resp = _mock_response(401, ERROR_BODY)
        with (
            patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp),
            patch("dbt_cloud.cli.click.echo") as mock_echo,
        ):
            runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        err_calls = [c for c in mock_echo.call_args_list if c.kwargs.get("err")]
        assert len(err_calls) == 1
        assert "401" in str(err_calls[0])

    def test_delete_all_progress_uses_err_true(self, runner):
        list_body = {"status": {"code": 200}, "data": [{"id": 10}]}
        delete_body = {"status": {"code": 200}, "data": {}}

        list_resp = _mock_response(200, list_body)
        delete_resp = _mock_response(200, delete_body)

        with (
            patch("dbt_cloud.command.job.list.requests.get", return_value=list_resp),
            patch(
                "dbt_cloud.command.job.delete.requests.delete", return_value=delete_resp
            ),
            patch("dbt_cloud.cli.click.echo") as mock_echo,
        ):
            runner.invoke(
                cli,
                [
                    "job",
                    "delete-all",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--keep-jobs",
                    "[]",
                    "--yes",
                ],
            )

        err_calls = [c for c in mock_echo.call_args_list if c.kwargs.get("err")]
        err_messages = [str(c.args[0]) for c in err_calls]
        assert any("Jobs to delete" in m for m in err_messages)
        assert any("was deleted" in m for m in err_messages)

    def test_job_run_wait_status_uses_err_true(self, runner):
        trigger_body = {"status": {"code": 200}, "data": {"id": 99}}
        success_body = {
            "status": {"code": 200},
            "data": {"id": 99, "status": 10, "href": "http://x"},
        }

        trigger_resp = _mock_response(200, trigger_body)
        success_resp = _mock_response(200, success_body)

        with (
            patch("dbt_cloud.command.job.run.requests.post", return_value=trigger_resp),
            patch("dbt_cloud.command.run.get.requests.get", return_value=success_resp),
            patch("dbt_cloud.cli.click.echo") as mock_echo,
        ):
            runner.invoke(
                cli,
                [
                    "job",
                    "run",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "7",
                    "--wait",
                ],
            )

        err_calls = [c for c in mock_echo.call_args_list if c.kwargs.get("err")]
        err_messages = [str(c.args[0]) for c in err_calls]
        assert any("SUCCESS" in m or "RUNNING" in m for m in err_messages)


class TestReadonlyMode:
    """DBT_CLOUD_READONLY=true must block all mutating commands."""

    READONLY_ENV = {"DBT_CLOUD_READONLY": "true"}

    def _invoke_readonly(self, runner, args):
        return runner.invoke(cli, args, env=self.READONLY_ENV)

    def test_readonly_blocks_job_run(self, runner):
        result = self._invoke_readonly(
            runner,
            ["job", "run", "--api-token", "tok", "--account-id", "1", "--job-id", "7"],
        )
        assert result.exit_code == 1
        assert "readonly" in result.output.lower()

    def test_readonly_blocks_job_create(self, runner):
        result = self._invoke_readonly(
            runner,
            [
                "job",
                "create",
                "--api-token",
                "tok",
                "--account-id",
                "1",
                "--project-id",
                "2",
                "--environment-id",
                "3",
                "--name",
                "x",
                "--execute-steps",
                '["dbt run"]',
            ],
        )
        assert result.exit_code == 1
        assert "readonly" in result.output.lower()

    def test_readonly_blocks_job_delete(self, runner):
        result = self._invoke_readonly(
            runner,
            [
                "job",
                "delete",
                "--api-token",
                "tok",
                "--account-id",
                "1",
                "--job-id",
                "7",
            ],
        )
        assert result.exit_code == 1
        assert "readonly" in result.output.lower()

    def test_readonly_blocks_project_create(self, runner):
        result = self._invoke_readonly(
            runner,
            [
                "project",
                "create",
                "--api-token",
                "tok",
                "--account-id",
                "1",
                "--name",
                "x",
                "--type",
                "0",
            ],
        )
        assert result.exit_code == 1
        assert "readonly" in result.output.lower()

    def test_readonly_blocks_environment_create(self, runner):
        result = self._invoke_readonly(
            runner,
            [
                "environment",
                "create",
                "--api-token",
                "tok",
                "--account-id",
                "1",
                "--project-id",
                "2",
                "--name",
                "x",
                "--type",
                "deployment",
            ],
        )
        assert result.exit_code == 1
        assert "readonly" in result.output.lower()

    def test_readonly_allows_job_get(self, runner):
        mock_resp = _mock_response(200, SUCCESS_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = self._invoke_readonly(
                runner,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
            )
        assert result.exit_code == 0

    def test_readonly_allows_job_list(self, runner):
        list_body = {"status": {"code": 200}, "data": []}
        mock_resp = _mock_response(200, list_body)
        with patch("dbt_cloud.command.job.list.requests.get", return_value=mock_resp):
            result = self._invoke_readonly(
                runner,
                ["job", "list", "--api-token", "tok", "--account-id", "1"],
            )
        assert result.exit_code == 0

    def test_readonly_false_allows_mutating(self, runner):
        """DBT_CLOUD_READONLY=false must not block commands."""
        mock_resp = _mock_response(200, SUCCESS_BODY)
        with patch("dbt_cloud.command.job.get.requests.get", return_value=mock_resp):
            result = runner.invoke(
                cli,
                [
                    "job",
                    "get",
                    "--api-token",
                    "tok",
                    "--account-id",
                    "1",
                    "--job-id",
                    "42",
                ],
                env={"DBT_CLOUD_READONLY": "false"},
            )
        assert result.exit_code == 0
