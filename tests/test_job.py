from dbt_cloud.job import DbtCloudJobRunArgs, DbtCloudJob
from dbt_cloud.command import DbtCloudJobCreateCommand
from dbt_cloud.serde import json_to_dict


def test_job_run_args_steps_override_is_none_if_empty():
    args = DbtCloudJobRunArgs(steps_override=())
    assert args.steps_override is None


def test_job_create_command_import_from_json(job_get_response):
    job_dict = job_get_response["data"]
    command = DbtCloudJobCreateCommand(**job_dict)
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


def test_job_to_file_and_from_file(shared_datadir, mock_job_api, job):
    path = shared_datadir / "job.json"
    job.to_file(path)
    job_imported = DbtCloudJob.from_file(file_path=path, api_token=job.api_token)
    assert job_imported.job_id is None
    job_imported.job_id = job.job_id
    assert job.dict() == job_imported.dict()


def test_job_export_import(shared_datadir, mock_job_api, job):
    path = shared_datadir / "job.json"
    job.to_file(path, exclude=["id"])

    job_create_kwargs = json_to_dict(path.read_text())
    command = DbtCloudJobCreateCommand(**job_create_kwargs)
    command.execute()
