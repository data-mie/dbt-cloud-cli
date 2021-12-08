# dbt-cloud-cli

`dbt-cloud-cli` is a command line interface for [dbt Cloud API v2.0](https://docs.getdbt.com/dbt-cloud/api-v2). It abstracts the REST API calls in an easy-to-use interface that can be incorporated into automated and manual (ad-hoc) workloads. For example, [dbt-cloud job run](#dbt-cloud-job-run) can be used in a CI/CD workflow (e.g., Github Actions) to trigger a dbt Cloud job that runs and tests the changes in a commit branch.

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
* [dbt-cloud run get](#dbt-cloud-run-get)

## dbt-cloud job run
This command triggers a dbt Cloud job run and returns a status JSON response. For more information on the API endpoint arguments and response, run `dbt-cloud job run --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun).

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

## dbt-cloud run get
This command prints a dbt Cloud run status JSON response. For more information on the API endpoint arguments and response, run `dbt-cloud run get --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getRunById).

### Usage

```bash
>> dbt-cloud run get --run-id 36053848
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
    "id": 36053848,
    "trigger_id": 36768889,
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
    "executed_by_thread_id": "dbt-run-36053848-84vsp",
    "deferring_run_id": null,
    "artifacts_saved": true,
    "artifact_s3_path": "prod/runs/36053848/artifacts/target",
    "has_docs_generated": false,
    "has_sources_generated": false,
    "notifications_sent": true,
    "blocked_by": [],
    "scribe_enabled": true,
    "created_at": "2021-12-07 10:32:24.326116+00:00",
    "updated_at": "2021-12-07 10:34:14.507280+00:00",
    "dequeued_at": "2021-12-07 10:33:54.599925+00:00",
    "started_at": "2021-12-07 10:34:01.982824+00:00",
    "finished_at": "2021-12-07 10:34:14.435474+00:00",
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
    "duration": "00:01:50",
    "queued_duration": "00:01:37",
    "run_duration": "00:00:12",
    "duration_humanized": "1 minute, 50 seconds",
    "queued_duration_humanized": "1 minute, 37 seconds",
    "run_duration_humanized": "12 seconds",
    "created_at_humanized": "34 minutes, 20 seconds ago",
    "finished_at_humanized": "32 minutes, 29 seconds ago",
    "job_id": 43167
  }
}
```