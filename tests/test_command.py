import pytest
from dbt_cloud.command.command import translate_click_options


@pytest.mark.parametrize(
    "fixture_name",
    # TODO: How to dynamically get markers from the fixtures?
    [
        pytest.param("job_get", marks=pytest.mark.job),
        pytest.param("job_create", marks=pytest.mark.job),
        pytest.param("job_delete", marks=pytest.mark.job),
        pytest.param("job_run", marks=pytest.mark.job),
        pytest.param("run_get", marks=pytest.mark.run),
        pytest.param("run_list_artifacts", marks=pytest.mark.run),
        pytest.param("run_get_artifact", marks=pytest.mark.run),
    ],
)
class TestCommandV2:
    def test_execute(self, fixture_name, mock_dbt_cloud_api, request):
        command_fixture = request.getfixturevalue(fixture_name)
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
