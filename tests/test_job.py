import pytest
from dbt_cloud.command import DbtCloudJobCreateCommand, DbtCloudJobRunCommand
from dbt_cloud.command.job.create import JobTypeEnum

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
    assert command.triggers.git_provider_webhook == False
    assert command.settings.threads == 4
    assert command.settings.target_name == "default"
    assert command.schedule.cron == "0 * * * *"
    assert command.schedule.date.type.value == "every_day"
    assert command.schedule.time.type.value == "every_hour"
    assert command.execution.timeout_seconds == 0
    assert command.run_generate_sources == False
    assert command.lifecycle_webhooks == False
    assert command.deferring_job_definition_id is None


def test_job_create_command_new_fields_in_payload():
    command = DbtCloudJobCreateCommand(
        api_token="foo",
        account_id=123456,
        project_id=123457,
        environment_id=49819,
        name="CI job",
        execute_steps=["dbt run"],
        description="Runs on every PR",
        job_type=JobTypeEnum.CI,
        execution={"timeout_seconds": 300},
        run_generate_sources=True,
        run_compare_changes=True,
        run_lint=True,
        errors_on_lint_failure=True,
        lifecycle_webhooks=True,
        triggers_on_draft_pr=True,
        deferring_environment_id=99,
        triggers={"github_webhook": False, "schedule": False, "custom_branch_only": False, "git_provider_webhook": True, "on_merge": True},
    )
    payload = command.get_payload()
    assert payload["description"] == "Runs on every PR"
    assert payload["job_type"] == "ci"
    assert payload["execution"]["timeout_seconds"] == 300
    assert payload["run_generate_sources"] == True
    assert payload["run_compare_changes"] == True
    assert payload["run_lint"] == True
    assert payload["errors_on_lint_failure"] == True
    assert payload["lifecycle_webhooks"] == True
    assert payload["triggers_on_draft_pr"] == True
    assert payload["deferring_environment_id"] == 99
    assert payload["triggers"]["git_provider_webhook"] == True
    assert payload["triggers"]["on_merge"] == True
