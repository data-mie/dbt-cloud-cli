import pytest
from dbt_cloud.command.command import translate_click_options


@pytest.fixture
def command(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def response(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "command,response",
    [
        pytest.param("job_get_command", "job_get_response", marks=pytest.mark.job),
        pytest.param(
            "job_create_command", "job_create_response", marks=pytest.mark.job
        ),
        pytest.param(
            "job_delete_command", "job_delete_response", marks=pytest.mark.job
        ),
        pytest.param("job_run_command", "job_run_response", marks=pytest.mark.job),
        pytest.param("run_get_command", "run_get_response", marks=pytest.mark.run),
        pytest.param(
            "run_list_artifacts_command",
            "run_list_artifacts_response",
            marks=pytest.mark.run,
        ),
        pytest.param(
            "run_get_artifact_command",
            "run_get_artifact_response",
            marks=pytest.mark.run,
        ),
    ],
    indirect=True,
)
class TestCommand:
    def test_execute(self, command, response, mock_dbt_cloud_api):
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
