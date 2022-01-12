import pytest
from pytest_cases import parametrize
from dbt_cloud.command.command import translate_click_options


@pytest.fixture
def command_fixture(request):
    fixt = request.getfixturevalue(request.param)
    return pytest.param(*fixt.values, marks=fixt.marks)


@pytest.mark.parametrize(
    "command_fixture",
    [
        "job_get",
        "job_create",
        "job_delete",
        "job_run",
        "run_get",
        "run_list_artifacts",
        "run_get_artifact",
    ],
    indirect=True,
)
class TestCommandV2:
    def test_execute(self, command_fixture, mock_dbt_cloud_api):
        print(command_fixture.marks)
        command, response, _ = command_fixture.values
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
