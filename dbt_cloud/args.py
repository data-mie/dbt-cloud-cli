import click
import os
from pydantic import BaseModel, validator, Field
from dbt_cloud.serde import json_to_dict


class ArgsBaseModel(BaseModel):
    @classmethod
    def click_options(cls, function, key_prefix: str = ""):
        for key, field in reversed(cls.__fields__.items()):
            try:
                is_nested_object = issubclass(field.type_, BaseModel)
            except TypeError:
                is_nested_object = False

            if is_nested_object:
                function = field.type_.click_options(
                    function, key_prefix=f"{key_prefix}_{key}".strip("_")
                )
            else:
                help = field.field_info.description or ""
                key = f"{key_prefix}_{key}".replace("_", "-").strip("-")
                try:
                    is_list_arg = issubclass(field.outer_type_.__origin__, list)
                except AttributeError:
                    is_list_arg = False
                function = click.option(
                    f"--{key}",
                    type=field.type_,
                    required=field.required,
                    default=field.default,
                    multiple=is_list_arg,
                    help=help,
                )(function)
        return function

    @validator("*", pre=True)
    def field_not_none(cls, value, field):
        if field.default and value is None:
            return field.default
        elif field.default_factory and value is None:
            return field.default_factory()
        else:
            return value

    def get_payload(self, exclude=["api_token", "account_id", "job_id"]) -> dict:
        payload = self.json(exclude=set(exclude))
        return json_to_dict(payload)


class DbtCloudArgsBaseModel(ArgsBaseModel):
    api_token: str = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_API_TOKEN"],
        description="API authentication key (default: 'DBT_CLOUD_API_TOKEN' environment variable)",
    )
    account_id: int = Field(
        default_factory=lambda: os.environ["DBT_CLOUD_ACCOUNT_ID"],
        description="Numeric ID of the Account that the job belongs to (default: 'DBT_CLOUD_ACCOUNT_ID' environment variable)",
    )
