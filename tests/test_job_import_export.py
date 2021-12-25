import json
from dbt_cloud.serde import json_to_dict
from dbt_cloud.job import DbtCloudJob, DbtCloudJobCreateArgs


def test_job_args_import_from_json(job_get_response):
    job_dict = job_get_response["data"]
    args = DbtCloudJobCreateArgs(**job_dict)
    assert args.environment_id == 49819
    assert args.account_id == 123456
    assert args.project_id == 123457
    assert args.name == "Do nothing!"
    assert args.execute_steps == ["dbt run -s not_a_model"]
    assert not args.generate_docs
    assert args.dbt_version is None
    assert not args.triggers.github_webhook
    assert args.triggers.custom_branch_only
    assert not args.triggers.schedule
    assert args.settings.threads == 4
    assert args.settings.target_name == "default"
    assert args.schedule.cron == "0 * * * *"
    assert args.schedule.date.type.value == "every_day"
    assert args.schedule.time.type.value == "every_hour"


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
    job_create_args = DbtCloudJobCreateArgs(**job_create_kwargs)
    job_kwargs = {**job.dict(), "job_id": None}
    job_new = DbtCloudJob(**job_kwargs)
    job_new.create(job_create_args)
