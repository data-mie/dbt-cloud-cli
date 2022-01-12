import pytest


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
    ],
    indirect=True,
)
class TestCommand:
    def test_execute(self, command, response, mock_job_api):
        actual_response = command.execute()
        actual_response.raise_for_status()
        assert actual_response.json() == response
