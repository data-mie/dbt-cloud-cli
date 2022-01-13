import pytest
from dbt_cloud.command import DbtCloudJobCreateCommand, DbtCloudJobRunCommand

pytestmark = pytest.mark.job


def test_job_run_command_steps_override_is_none_if_empty():
    command = DbtCloudJobRunCommand(
        api_token="foo", account_id=123, job_id=123, steps_override=()
    )
    assert command.steps_override is None


def test_job_create_command_import_from_json(job_get):
    response = job_get.values[2]
    job_dict = response["data"]
    command = DbtCloudJobCreateCommand(api_token="foo", **job_dict)
    assert command.environment_id == 49819
    assert command.account_id == 123456
    assert command.project_id == 123457
    assert command.name == "Do nothing!"
    assert command.execute_steps == ["dbt run -s not_a_model"]
    assert not command.generate_docs
    assert command.dbt_version is None
    assert not command.triggers.github_webhook
    assert command.triggers.custom_branch_only
    assert not command.triggers.schedule
    assert command.settings.threads == 4
    assert command.settings.target_name == "default"
    assert command.schedule.cron == "0 * * * *"
    assert command.schedule.date.type.value == "every_day"
    assert command.schedule.time.type.value == "every_hour"
