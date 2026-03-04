import click
from collections import OrderedDict
from typing import Union, get_args, get_origin
from mergedeep import merge
from pydantic import model_validator, BaseModel, PrivateAttr
from pydantic_core import PydanticUndefined
from dbt_cloud.serde import json_to_dict
from dbt_cloud.field import (
    API_TOKEN_FIELD,
    ACCOUNT_ID_FIELD,
    PROJECT_ID_FIELD,
    DBT_CLOUD_HOST_FIELD,
)


def _unwrap_optional(annotation):
    """Unwrap Optional[X] to X; return annotation unchanged otherwise."""
    if get_origin(annotation) is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation


def translate_click_options(**kwargs) -> dict:
    """Translates click options to pydantic model inputs."""
    items = []
    for key, value in kwargs.items():
        key_split = key.split("__")
        item = value
        for key_part in reversed(key_split):
            item = {key_part: item}
        items.append(item)
    kwargs_translated = merge(*items)
    return kwargs_translated


class ClickBaseModel(BaseModel):
    @classmethod
    def click_options(cls, function, key_prefix: str = ""):
        for key, field in reversed(OrderedDict(cls.model_fields).items()):
            annotation = field.annotation
            inner_type = _unwrap_optional(annotation)

            try:
                is_nested_object = issubclass(inner_type, BaseModel)
            except TypeError:
                is_nested_object = False

            if is_nested_object:
                function = inner_type.click_options(
                    function, key_prefix=f"{key_prefix}__{key}".strip("_")
                )
            else:
                schema_extra = field.json_schema_extra or {}
                if schema_extra.get("exclude_from_click_options", False):
                    continue

                help = field.description or ""
                kwarg_name = f"{key_prefix}__{key}".strip("_")
                key_display = kwarg_name.replace("__", "-").replace("_", "-")

                click_cls = schema_extra.get("click_cls")
                override_cls = click_cls is not None

                try:
                    is_list_arg = get_origin(inner_type) is list and not override_cls
                except Exception:
                    is_list_arg = False

                default = (
                    None if field.default is PydanticUndefined else field.default
                )

                option_kwargs = {
                    "required": field.is_required(),
                    "default": default,
                    "multiple": is_list_arg,
                    "is_flag": schema_extra.get("is_flag", False),
                    "help": help,
                }
                if override_cls:
                    option_kwargs["cls"] = click_cls
                else:
                    option_kwargs["type"] = inner_type

                function = click.option(
                    f"--{key_display}",
                    kwarg_name,
                    **option_kwargs,
                )(function)
        return function

    @model_validator(mode="before")
    @classmethod
    def field_not_none(cls, values):
        if not isinstance(values, dict):
            return values
        for key, field in cls.model_fields.items():
            if key in values and values[key] is None:
                if field.default is not PydanticUndefined and field.default is not None:
                    values[key] = field.default
                elif field.default_factory is not None:
                    values[key] = field.default_factory()
        return values

    @classmethod
    def from_click_options(cls, **kwargs):
        kwargs_translated = translate_click_options(**kwargs)
        return cls(**kwargs_translated)

    @classmethod
    def get_description(cls) -> str:
        return cls.__doc__.strip()


class DbtCloudCommand(ClickBaseModel):
    api_token: str = API_TOKEN_FIELD
    dbt_cloud_host: str = DBT_CLOUD_HOST_FIELD
    _api_version: str = PrivateAttr("v3")

    @property
    def request_headers(self) -> dict:
        return {"Authorization": f"Token {self.api_token}"}

    @property
    def api_url(self) -> str:
        return f"https://{self.dbt_cloud_host}/api/{self._api_version}"

    def get_payload(
        self, exclude=["api_token", "dbt_cloud_host"], exclude_empty: bool = False
    ) -> dict:
        payload_dict = self.model_dump(mode="json", exclude=set(exclude))
        if exclude_empty:
            payload_dict = {
                key: value for key, value in payload_dict.items() if value is not None
            }
        return payload_dict


class DbtCloudAccountCommand(DbtCloudCommand):
    account_id: int = ACCOUNT_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/accounts/{self.account_id}"


class DbtCloudProjectCommand(DbtCloudAccountCommand):
    project_id: int = PROJECT_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/projects/{self.project_id}"
