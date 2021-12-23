import json


def dict_to_json(value: dict) -> str:
    return json.dumps(value, indent=2)


def json_to_dict(value: str) -> dict:
    return json.loads(value)
