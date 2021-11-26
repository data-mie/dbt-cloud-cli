import click
from pydantic import BaseModel, validator


class ArgsBaseModel(BaseModel):
    @classmethod
    def click_options(cls, function):
        for key, field in reversed(cls.__fields__.items()):
            function = click.option(
                f"--{key.replace('_', '-')}",
                type=field.type_,
                required=field.required,
                help=field.field_info.description,
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

    def get_payload(self) -> dict:
        payload = self.dict()
        exclude_keys = ["api_token", "account_id", "job_id"]
        payload = {
            key: value
            for key, value in payload.items()
            if value is not None and key not in exclude_keys
        }
        return payload
