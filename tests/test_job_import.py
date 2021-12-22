import json
from dbt_cloud.job import DbtCloudJobCreateArgs


def test_job_args_import_from_json(shared_datadir):
    response_file = shared_datadir / "job_get_response.json"
    response_json = response_file.read_text()
    response_dict = json.loads(response_json)
    job_dict = response_dict["data"]
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
