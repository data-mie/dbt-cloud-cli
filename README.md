# dbt-cloud-cli

This is a work a in progress for a dbt Cloud command line interface!

## Installation

`dbt-cloud-cli` has been tested on Python 3.8 but it should work on Python>=3.6.

Installation from PyPI:

    pip install dbt-cloud-cli

Installation from GitHub:

    pip install git+https://github.com/data-mie/dbt-cloud-cli.git

## Environment variables

The following environment variables are used as argument defaults:

* `DBT_CLOUD_API_TOKEN` (`--api-token`)
* `DBT_CLOUD_ACCOUNT_ID` (`--account-id`)
* `DBT_CLOUD_JOB_ID` (`--job-id`)

# Commands

* [dbt-cloud job run](#dbt-cloud-job-run)

## dbt-cloud job run
This command triggers a dbt Cloud job run and returns a status JSON response.

### Arguments

Run `dbt-cloud job run --help` to get a list of the arguments. Also, see [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun).

### Response

See [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun).

### Usage

```bash
>> dbt-cloud job run --job-id 43167 --cause "My first run!" --wait
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: STARTING ...
Job 43167 run 34929305: RUNNING ...
Job 43167 run 34929305: SUCCESS ...
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "id": 34929305,
    "trigger_id": 35644346,
    "account_id": REDACTED,
    "environment_id": 49819,
    "project_id": REDACTED,
    "job_definition_id": 43167,
    "status": 10,
    "dbt_version": "0.21.0",
    "git_branch": "main",
    "git_sha": "981c5cf1ba299e942c6c277c38c8dec9b0738dd0",
    "status_message": null,
    "owner_thread_id": null,
    "executed_by_thread_id": "dbt-run-34929305-dcmbq",
    "deferring_run_id": null,
    "artifacts_saved": true,
    "artifact_s3_path": "prod/runs/34929305/artifacts/target",
    "has_docs_generated": false,
    "has_sources_generated": false,
    "notifications_sent": true,
    "blocked_by": [],
    "scribe_enabled": true,
    "created_at": "2021-11-26 16:48:41.431645+00:00",
    "updated_at": "2021-11-26 16:49:33.078918+00:00",
    "dequeued_at": "2021-11-26 16:49:15.670558+00:00",
    "started_at": "2021-11-26 16:49:20.535987+00:00",
    "finished_at": "2021-11-26 16:49:32.996703+00:00",
    "last_checked_at": null,
    "last_heartbeat_at": null,
    "should_start_at": null,
    "trigger": null,
    "job": null,
    "environment": null,
    "run_steps": [],
    "status_humanized": "Success",
    "in_progress": false,
    "is_complete": true,
    "is_success": true,
    "is_error": false,
    "is_cancelled": false,
    "href": REDACTED,
    "duration": "00:00:51",
    "queued_duration": "00:00:39",
    "run_duration": "00:00:12",
    "duration_humanized": "51 seconds",
    "queued_duration_humanized": "39 seconds",
    "run_duration_humanized": "12 seconds",
    "created_at_humanized": "1 minute ago",
    "finished_at_humanized": "9 seconds ago",
    "job_id": 43167
  }
}
```