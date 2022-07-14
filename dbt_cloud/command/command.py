import click
from collections import OrderedDict
from mergedeep import merge
from pydantic import validator, BaseModel, PrivateAttr
from dbt_cloud.serde import json_to_dict
from dbt_cloud.field import API_TOKEN_FIELD, ACCOUNT_ID_FIELD, DBT_CLOUD_HOST_FIELD


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
        for key, field in reversed(OrderedDict(cls.__fields__).items()):
            try:
                is_nested_object = issubclass(field.type_, BaseModel)
            except TypeError:
                is_nested_object = False

            if is_nested_object:
                function = field.type_.click_options(
                    function, key_prefix=f"{key_prefix}__{key}".strip("_")
                )
            else:
                if (
                    field.field_info.extra.get("exclude_from_click_options", False)
                    or field.field_info.const
                ):
                    continue
                help = field.field_info.description or ""
                kwarg_name = f"{key_prefix}__{key}".strip("_")
                key = kwarg_name.replace("__", "-").replace("_", "-")

                cls = field.field_info.extra.get("click_cls")
                override_cls = cls is not None

                try:
                    is_list_arg = (
                        issubclass(field.outer_type_.__origin__, list)
                        and not override_cls
                    )
                except AttributeError:
                    is_list_arg = False

                option_kwargs = {
                    "required": field.required,
                    "default": field.default,
                    "multiple": is_list_arg,
                    "is_flag": field.field_info.extra.get("is_flag", False),
                    "help": help,
                }
                if override_cls:
                    option_kwargs["cls"] = cls
                else:
                    option_kwargs["type"] = field.type_

                function = click.option(
                    f"--{key}",
                    kwarg_name,
                    **option_kwargs,
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
    _api_version: str = PrivateAttr("v2")

    @property
    def request_headers(self) -> dict:
        return {"Authorization": f"Token {self.api_token}"}

    @property
    def api_url(self) -> str:
        return f"https://{self.dbt_cloud_host}/api/{self._api_version}"

    def get_payload(self, exclude=["api_token", "dbt_cloud_host"]) -> dict:
        payload = self.json(exclude=set(exclude))
        return json_to_dict(payload)


class DbtCloudAccountCommand(DbtCloudCommand):
    account_id: int = ACCOUNT_ID_FIELD

    @property
    def api_url(self) -> str:
        return f"{super().api_url}/accounts/{self.account_id}"
