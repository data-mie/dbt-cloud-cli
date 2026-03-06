"""
Pre-built tool definitions for AI agent frameworks.

Generates OpenAI function calling and Anthropic tool use schemas directly from
the Pydantic command models, and provides a unified execute_tool_call() entry
point for library-mode usage.

Usage (OpenAI):
    from dbt_cloud.tools import get_openai_tools, execute_tool_call
    tools = get_openai_tools()
    result = execute_tool_call("job_run", {"account_id": 123, "job_id": 456})

Usage (Anthropic):
    from dbt_cloud.tools import get_anthropic_tools, execute_tool_call
    tools = get_anthropic_tools()
    result = execute_tool_call("job_get", {"account_id": 123, "job_id": 456})
"""

import os
from enum import Enum
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from dbt_cloud.command import (
    DbtCloudAccountGetCommand,
    DbtCloudAccountListCommand,
    DbtCloudAuditLogGetCommand,
    DbtCloudConnectionCreateCommand,
    DbtCloudConnectionDeleteCommand,
    DbtCloudConnectionGetCommand,
    DbtCloudConnectionListCommand,
    DbtCloudEnvironmentCreateCommand,
    DbtCloudEnvironmentDeleteCommand,
    DbtCloudEnvironmentGetCommand,
    DbtCloudEnvironmentListCommand,
    DbtCloudJobCreateCommand,
    DbtCloudJobDeleteCommand,
    DbtCloudJobGetCommand,
    DbtCloudJobListCommand,
    DbtCloudJobRunCommand,
    DbtCloudMetadataQueryCommand,
    DbtCloudProjectCreateCommand,
    DbtCloudProjectDeleteCommand,
    DbtCloudProjectGetCommand,
    DbtCloudProjectListCommand,
    DbtCloudProjectUpdateCommand,
    DbtCloudRunCancelCommand,
    DbtCloudRunGetArtifactCommand,
    DbtCloudRunGetCommand,
    DbtCloudRunListArtifactsCommand,
    DbtCloudRunListCommand,
)

# Registry mapping tool name → command class.
# Tool names follow the pattern <resource>_<action> (e.g. job_run, run_get).
TOOL_REGISTRY: dict[str, type] = {
    "job_get": DbtCloudJobGetCommand,
    "job_list": DbtCloudJobListCommand,
    "job_create": DbtCloudJobCreateCommand,
    "job_delete": DbtCloudJobDeleteCommand,
    "job_run": DbtCloudJobRunCommand,
    "run_get": DbtCloudRunGetCommand,
    "run_list": DbtCloudRunListCommand,
    "run_cancel": DbtCloudRunCancelCommand,
    "run_list_artifacts": DbtCloudRunListArtifactsCommand,
    "run_get_artifact": DbtCloudRunGetArtifactCommand,
    "project_get": DbtCloudProjectGetCommand,
    "project_list": DbtCloudProjectListCommand,
    "project_create": DbtCloudProjectCreateCommand,
    "project_delete": DbtCloudProjectDeleteCommand,
    "project_update": DbtCloudProjectUpdateCommand,
    "environment_get": DbtCloudEnvironmentGetCommand,
    "environment_list": DbtCloudEnvironmentListCommand,
    "environment_create": DbtCloudEnvironmentCreateCommand,
    "environment_delete": DbtCloudEnvironmentDeleteCommand,
    "account_get": DbtCloudAccountGetCommand,
    "account_list": DbtCloudAccountListCommand,
    "audit_log_get": DbtCloudAuditLogGetCommand,
    "connection_get": DbtCloudConnectionGetCommand,
    "connection_list": DbtCloudConnectionListCommand,
    "connection_create": DbtCloudConnectionCreateCommand,
    "connection_delete": DbtCloudConnectionDeleteCommand,
    "metadata_query": DbtCloudMetadataQueryCommand,
}

# Fields that are infrastructure concerns — injected at execute time, not by the agent.
_INFRA_FIELDS = {"api_token", "dbt_cloud_host", "timeout"}


def _annotation_to_json_schema(annotation: Any) -> dict:
    """Convert a Python type annotation to a JSON schema dict."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[X] / Union[X, None]
    if origin is Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _annotation_to_json_schema(non_none[0])
        return {}

    # List[X]
    if origin is list:
        item_schema = _annotation_to_json_schema(args[0]) if args else {}
        return {"type": "array", "items": item_schema}

    # Nested Pydantic model — recurse
    try:
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return _model_to_json_schema(annotation)
    except TypeError:
        pass

    # Enum → string with enum values
    try:
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return {"type": "string", "enum": [e.value for e in annotation]}
    except TypeError:
        pass

    # Primitives
    _type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
    if annotation in _type_map:
        return {"type": _type_map[annotation]}

    return {}


def _model_to_json_schema(cls: type, strip_infra: bool = False) -> dict:
    """Build a JSON schema object for a Pydantic model class.

    Args:
        cls: The Pydantic model class.
        strip_infra: When True, remove infrastructure fields and excluded fields.
    """
    props: dict[str, Any] = {}
    required: list[str] = []

    for name, field in cls.model_fields.items():
        extra = field.json_schema_extra or {}
        if strip_infra and (
            name in _INFRA_FIELDS or extra.get("exclude_from_click_options")
        ):
            continue

        field_schema = _annotation_to_json_schema(field.annotation)
        if field.description:
            field_schema["description"] = field.description
        if field.is_required():
            required.append(name)

        props[name] = field_schema

    result: dict[str, Any] = {"type": "object", "properties": props}
    if required:
        result["required"] = required
    return result


def _get_tool_schema(command_cls: type) -> dict:
    """Return a cleaned JSON schema for the given command class.

    Strips infrastructure fields (api_token, dbt_cloud_host, timeout) and
    fields marked exclude_from_click_options (auto-assigned by the API).
    """
    return _model_to_json_schema(command_cls, strip_infra=True)


def get_openai_tools(include: list[str] | None = None) -> list[dict]:
    """Return tool definitions in OpenAI function calling format.

    Args:
        include: Optional list of tool names to include. Defaults to all tools.

    Returns:
        List of dicts with ``{"type": "function", "function": {...}}`` shape.
    """
    tools = []
    for name, cls in TOOL_REGISTRY.items():
        if include is not None and name not in include:
            continue
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": cls.get_description(),
                    "parameters": _get_tool_schema(cls),
                },
            }
        )
    return tools


def get_anthropic_tools(include: list[str] | None = None) -> list[dict]:
    """Return tool definitions in Anthropic tool use format.

    Args:
        include: Optional list of tool names to include. Defaults to all tools.

    Returns:
        List of dicts with ``{"name": ..., "description": ..., "input_schema": {...}}`` shape.
    """
    tools = []
    for name, cls in TOOL_REGISTRY.items():
        if include is not None and name not in include:
            continue
        tools.append(
            {
                "name": name,
                "description": cls.get_description(),
                "input_schema": _get_tool_schema(cls),
            }
        )
    return tools


def execute_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool call and return the API response as a dict.

    Infrastructure fields (api_token, dbt_cloud_host) are injected from
    environment variables if not present in tool_input.

    Args:
        tool_name: One of the keys in TOOL_REGISTRY (e.g. ``"job_run"``).
        tool_input: Dict of arguments for the command (excluding api_token etc.).

    Returns:
        The parsed JSON response body from the dbt Cloud API.

    Raises:
        ValueError: If tool_name is not in TOOL_REGISTRY.
        requests.HTTPError: If the API returns a non-2xx status.
    """
    cls = TOOL_REGISTRY.get(tool_name)
    if cls is None:
        raise ValueError(
            f"Unknown tool: {tool_name!r}. Available tools: {sorted(TOOL_REGISTRY)}"
        )

    kwargs = dict(tool_input)
    kwargs.setdefault("api_token", os.environ.get("DBT_CLOUD_API_TOKEN", ""))
    kwargs.setdefault(
        "dbt_cloud_host",
        os.environ.get("DBT_CLOUD_HOST", "https://cloud.getdbt.com"),
    )

    command = cls(**kwargs)
    response = command.execute()
    response.raise_for_status()
    return response.json()
