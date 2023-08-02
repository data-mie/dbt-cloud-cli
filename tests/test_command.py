import pytest
from typing import Optional
from dbt_cloud.command.command import translate_click_options, DbtCloudCommand
from .conftest import COMMAND_TEST_CASES


@pytest.mark.parametrize(
    "test_case_name,command,response,http_method", COMMAND_TEST_CASES
)
class TestCommand:
    def test_execute(
        self, test_case_name, command, response, http_method, mock_dbt_cloud_api
    ):
        actual_response = command.execute()
        actual_response.raise_for_status()
        assert actual_response.json() == response


def test_translate_nested_click_options():
    kwargs = {
        "project_id": 12345,
        "settings__threads": 4,
        "foo__bar__baz": "apple",
        "foo__baz": "orange",
    }
    kwargs_translated = translate_click_options(**kwargs)
    assert kwargs_translated == {
        "project_id": 12345,
        "settings": {"threads": 4},
        "foo": {"baz": "orange", "bar": {"baz": "apple"}},
    }


class PayloadCommand(DbtCloudCommand):
    id: Optional[int]


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (
            {
                "api_token": "123",
                "dbt_cloud_host": "https://cloud.getdbt.com",
                "id": 12345,
            },
            {
                "api_token": "123",
                "dbt_cloud_host": "https://cloud.getdbt.com",
                "id": 12345,
            },
        ),
        (
            {
                "api_token": "123",
                "dbt_cloud_host": "https://cloud.getdbt.com",
                "id": None,
            },
            {
                "api_token": "123",
                "dbt_cloud_host": "https://cloud.getdbt.com",
            },
        ),
    ],
)
def test_dbt_cloud_command_get_payload(kwargs, expected):
    command = PayloadCommand(**kwargs)
    assert command.get_payload(exclude=[], exclude_empty=True) == expected
