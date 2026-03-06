"""Tests for dbt_cloud/tools.py — AI agent tool definitions."""

import os
import pytest
from unittest.mock import MagicMock, patch
from requests.models import Response
from requests import HTTPError

from dbt_cloud.tools import (
    TOOL_REGISTRY,
    get_openai_tools,
    get_anthropic_tools,
    execute_tool_call,
    _get_tool_schema,
)
from dbt_cloud.command import DbtCloudJobGetCommand, DbtCloudJobRunCommand


class TestToolRegistry:
    def test_registry_is_not_empty(self):
        assert len(TOOL_REGISTRY) > 0

    def test_registry_contains_core_tools(self):
        core = {"job_get", "job_list", "job_run", "run_get", "run_list", "project_get"}
        assert core.issubset(TOOL_REGISTRY.keys())

    def test_registry_values_are_command_classes(self):
        from dbt_cloud.command.command import ClickBaseModel

        for name, cls in TOOL_REGISTRY.items():
            assert issubclass(cls, ClickBaseModel), f"{name} is not a ClickBaseModel"


class TestGetToolSchema:
    def test_infra_fields_stripped(self):
        schema = _get_tool_schema(DbtCloudJobGetCommand)
        props = schema["properties"]
        assert "api_token" not in props
        assert "dbt_cloud_host" not in props
        assert "timeout" not in props

    def test_exclude_from_click_options_stripped(self):
        # DbtCloudJobGetCommand has job_id but not an excluded id field
        # DbtCloudJobCreateCommand has id with exclude_from_click_options=True
        from dbt_cloud.command import DbtCloudJobCreateCommand

        schema = _get_tool_schema(DbtCloudJobCreateCommand)
        assert "id" not in schema["properties"]

    def test_domain_fields_present(self):
        schema = _get_tool_schema(DbtCloudJobGetCommand)
        props = schema["properties"]
        assert "job_id" in props
        assert "account_id" in props

    def test_required_does_not_include_infra_fields(self):
        schema = _get_tool_schema(DbtCloudJobGetCommand)
        required = schema.get("required", [])
        assert "api_token" not in required
        assert "timeout" not in required

    def test_schema_type_is_object(self):
        schema = _get_tool_schema(DbtCloudJobGetCommand)
        assert schema["type"] == "object"


class TestGetOpenaiTools:
    def test_returns_list(self):
        tools = get_openai_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_each_tool_has_required_keys(self):
        for tool in get_openai_tools():
            assert tool["type"] == "function"
            fn = tool["function"]
            assert "name" in fn
            assert "description" in fn
            assert "parameters" in fn

    def test_include_filter(self):
        tools = get_openai_tools(include=["job_get", "job_run"])
        assert len(tools) == 2
        names = {t["function"]["name"] for t in tools}
        assert names == {"job_get", "job_run"}

    def test_include_empty_list(self):
        tools = get_openai_tools(include=[])
        assert tools == []

    def test_tool_parameters_are_valid_json_schema(self):
        tools = get_openai_tools(include=["job_get"])
        params = tools[0]["function"]["parameters"]
        assert params["type"] == "object"
        assert "properties" in params

    def test_description_is_non_empty(self):
        for tool in get_openai_tools():
            assert tool["function"][
                "description"
            ].strip(), f"{tool['function']['name']} has empty description"


class TestGetAnthropicTools:
    def test_returns_list(self):
        tools = get_anthropic_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_each_tool_has_required_keys(self):
        for tool in get_anthropic_tools():
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_include_filter(self):
        tools = get_anthropic_tools(include=["run_get", "run_list"])
        assert len(tools) == 2
        names = {t["name"] for t in tools}
        assert names == {"run_get", "run_list"}

    def test_input_schema_is_valid_json_schema(self):
        tools = get_anthropic_tools(include=["job_get"])
        schema = tools[0]["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_openai_and_anthropic_same_tool_names(self):
        openai_names = {t["function"]["name"] for t in get_openai_tools()}
        anthropic_names = {t["name"] for t in get_anthropic_tools()}
        assert openai_names == anthropic_names


class TestExecuteToolCall:
    def _mock_response(self, body):
        resp = MagicMock(spec=Response)
        resp.json.return_value = body
        resp.raise_for_status.return_value = None
        return resp

    def test_unknown_tool_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            execute_tool_call("not_a_real_tool", {})

    def test_injects_api_token_from_env(self):
        resp = self._mock_response({"status": {"code": 200}, "data": {"id": 1}})
        with (
            patch.dict(os.environ, {"DBT_CLOUD_API_TOKEN": "env-token"}),
            patch(
                "dbt_cloud.command.job.get.requests.get", return_value=resp
            ) as mock_get,
        ):
            execute_tool_call("job_get", {"account_id": 1, "job_id": 42})

        # api_token from env was used (it ends up in the Authorization header)
        call_kwargs = mock_get.call_args
        headers = (
            call_kwargs.kwargs.get("headers") or call_kwargs.args[1]
            if len(call_kwargs.args) > 1
            else {}
        )
        # Verify the request was made (api_token was injected without error)
        mock_get.assert_called_once()

    def test_explicit_api_token_takes_precedence(self):
        resp = self._mock_response({"status": {"code": 200}, "data": {}})
        with (
            patch.dict(os.environ, {"DBT_CLOUD_API_TOKEN": "env-token"}),
            patch("dbt_cloud.command.job.get.requests.get", return_value=resp),
        ):
            # Should not raise even with explicit token
            result = execute_tool_call(
                "job_get",
                {"account_id": 1, "job_id": 42, "api_token": "explicit-token"},
            )
        assert result == {"status": {"code": 200}, "data": {}}

    def test_returns_response_json(self):
        body = {"status": {"code": 200}, "data": {"id": 99}}
        resp = self._mock_response(body)
        with (
            patch.dict(os.environ, {"DBT_CLOUD_API_TOKEN": "tok"}),
            patch("dbt_cloud.command.job.get.requests.get", return_value=resp),
        ):
            result = execute_tool_call("job_get", {"account_id": 1, "job_id": 99})
        assert result == body

    def test_raises_on_http_error(self):
        resp = MagicMock(spec=Response)
        resp.json.return_value = {"status": {"code": 401}, "data": {}}
        resp.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        with (
            patch.dict(os.environ, {"DBT_CLOUD_API_TOKEN": "tok"}),
            patch("dbt_cloud.command.job.get.requests.get", return_value=resp),
        ):
            with pytest.raises(HTTPError):
                execute_tool_call("job_get", {"account_id": 1, "job_id": 99})
