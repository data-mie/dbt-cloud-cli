import pytest
from dbt_cloud.command.command import translate_click_options


@pytest.fixture
def command_fixture(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "command_fixture",
    [
        pytest.param(
            "job_get",
            marks=pytest.mark.job,
        ),
        pytest.param(
            "job_create",
            marks=pytest.mark.job,
        ),
        pytest.param(
            "job_delete",
            marks=pytest.mark.job,
        ),
        pytest.param(
            "job_run",
            marks=pytest.mark.job,
        ),
        pytest.param(
            "run_get",
            marks=pytest.mark.run,
        ),
        pytest.param(
            "run_list_artifacts",
            marks=pytest.mark.run,
        ),
        pytest.param(
            "run_get_artifact",
            marks=pytest.mark.run,
        ),
    ],
    indirect=True,
)
class TestCommandV2:
    def test_execute(self, command_fixture, mock_dbt_cloud_api):
        command, response, _ = command_fixture
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
