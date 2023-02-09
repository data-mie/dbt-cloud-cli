[![CircleCI](https://circleci.com/gh/data-mie/dbt-cloud-cli/tree/main.svg?style=svg)](https://circleci.com/gh/data-mie/dbt-cloud-cli/tree/main)

# dbt-cloud-cli

`dbt-cloud-cli` is a command line interface for [dbt Cloud API](https://docs.getdbt.com/dbt-cloud/api-v2). It abstracts the REST API calls in an easy-to-use interface that can be incorporated into automated and manual (ad-hoc) workloads. Here are some example use cases for `dbt-cloud-cli`:

1. Triggering a dbt Cloud job to run in a CI/CD pipeline: Use [dbt-cloud job run](#dbt-cloud-job-run) in a CI/CD workflow (e.g., Github Actions) to trigger a dbt Cloud job that runs and tests the changes in a commit branch
2. Setting up dbt Cloud jobs: Use [dbt-cloud job create](#dbt-cloud-job-create) to create standardized jobs between dbt Cloud projects. You can also use [dbt-cloud job export](#dbt-cloud-job-export) to export an existing job from one dbt Cloud project and then [dbt-cloud job import](#dbt-cloud-job-import) to import it to another.
3. Downloading run artifacts: Use [dbt-cloud run get-artifact](#dbt-cloud-run-get-artifact) to download run artifacts (e.g., `catalog.json`) from dbt Cloud.
4. Retrieving metadata: Use [dbt-cloud metadata query](#dbt-cloud-metadata-query) to retrieve metadata (e.g., model execution times, test results) from a dbt Cloud project.

## Installation

`dbt-cloud-cli` has been tested with the following Python versions:

* ✅ Python 3.6
* ✅ Python 3.7
* ✅ Python 3.8
* ✅ Python 3.9
* ✅ Python 3.10

Installation from PyPI:

```bash
pip install dbt-cloud-cli
```

Running in Docker:

```bash
docker run datamie/dbt-cloud-cli:latest
```

## Environment variables

The following environment variables are used as argument defaults:

* `DBT_CLOUD_HOST` (`--dbt-cloud-host`): dbt Cloud host (`cloud.getdbt.com` (multi-tenant instance) by default if the environment variable is not set)
* `DBT_CLOUD_API_TOKEN` (`--api-token`): API authentication key
* `DBT_CLOUD_ACCOUNT_ID` (`--account-id`): Numeric ID of the dbt Cloud account
* `DBT_CLOUD_JOB_ID` (`--job-id`): Numeric ID of a dbt Cloud job

# API coverage

<details>
  <summary><b>Coverage matrix</b></summary>

Group | API endpoint | Command | Description |
| --- | --- | --- | --- |
| Accounts | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getAccountById) | [dbt-cloud account get](#dbt-cloud-account-get)  | Retrieves dbt Cloud account information |
| Accounts | [https://cloud.getdbt.com/api/v2/accounts/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listAccounts) | [dbt-cloud account list](#dbt-cloud-account-list) | Retrieves all available accounts |
| Audit Logs | https://cloud.getdbt.com/api/v3/accounts/{accountId}/audit-logs/ | [dbt-cloud audit-log get](#dbt-cloud-audit-log-get) | Retrieves audit logs for the dbt Cloud account |
| Projects | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/projects/{projectId}](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getProjectById) | [dbt-cloud project get](#dbt-cloud-project-get) | Retrieves dbt Cloud project information |
| Projects | https://cloud.getdbt.com/api/v2/accounts/{accountId}/projects/ | [dbt-cloud project list](#dbt-cloud-project-list) | Returns a list of projects in the account |
| Environments | https://cloud.getdbt.com/api/v3/accounts/{accountId}/projects/{projectId}/environments | [dbt-cloud environment list](#dbt-cloud-environment-list) | Retrieves environments for a given project |
| Jobs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listJobsForAccount) | [dbt-cloud job list](#dbt-cloud-job-list) | Returns a list of jobs in the account |
| Jobs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/{jobId}/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getJobById) | [dbt-cloud job get](#dbt-cloud-job-get) | Returns the details of a dbt Cloud job |
| Jobs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/createJob) | [dbt-cloud job create](#dbt-cloud-job-create) | Creates a job in a dbt Cloud project |
| Jobs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/{jobId}/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/updateJobById) | `dbt-cloud job update` | Not implemented yet |
| Jobs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/{jobId}/run/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun) | [dbt-cloud job run](#dbt-cloud-job-run) | Triggers a dbt Cloud job run and returns a run status JSON response |
| Jobs | https://cloud.getdbt.com/api/v2/accounts/{accountId}/jobs/{jobId}/ | [dbt-cloud job delete](#dbt-cloud-job-delete) | Deletes a job in a dbt Cloud project |
| Runs | [https://cloud.getdbt.com/api/v2/accounts/{accountID}/runs](https://docs.getdbt.com/dbt-cloud/api-v2#tag/Runs/operation/listRunsForAccount) | [dbt-cloud run list](#dbt-cloud-run-list) | Returns a list of runs in the account |
| Runs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/runs/{runId}/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getRunById) | [dbt-cloud run get](#dbt-cloud-run-get) | Returns the details of a dbt Cloud run |
| Runs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/runs/{runId}/artifacts/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listArtifactsByRunId) | [dbt-cloud run list-artifacts](#dbt-cloud-run-list-artifacts) | Fetches a list of artifact files generated for a completed run |
| Runs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/runs/{runId}/artifacts/{path}](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getArtifactsByRunId) | [dbt-cloud run get-artifact](#dbt-cloud-run-get-artifact) | Fetches an artifact file from a completed run |
| Runs | [https://cloud.getdbt.com/api/v2/accounts/{accountId}/runs/{runId}/cancel/](https://docs.getdbt.com/dbt-cloud/api-v2#operation/cancelRunById) | [dbt-cloud run cancel](#dbt-cloud-run-cancel) | Cancels a dbt Cloud run |
| Metadata | [https://metadata.cloud.getdbt.com/graphql](https://docs.getdbt.com/docs/dbt-cloud/dbt-cloud-api/metadata/metadata-overview) | [dbt-cloud metadata query](#dbt-cloud-metadata-query) | Queries the dbt Cloud Metadata API using GraphQL |
</details>

# Commands

* [dbt-cloud account get](#dbt-cloud-account-get)
* [dbt-cloud account list](#dbt-cloud-account-list)
* [dbt-cloud audit-log get](#dbt-cloud-audit-log-get)
* [dbt-cloud project get](#dbt-cloud-project-get)
* [dbt-cloud project list](#dbt-cloud-project-list)
* [dbt-cloud environment list](#dbt-cloud-environment-list)
* [dbt-cloud job run](#dbt-cloud-job-run)
* [dbt-cloud job get](#dbt-cloud-job-get)
* [dbt-cloud job list](#dbt-cloud-job-list)
* [dbt-cloud job create](#dbt-cloud-job-create)
* [dbt-cloud job delete](#dbt-cloud-job-delete)
* [dbt-cloud job delete-all](#dbt-cloud-job-delete-all)
* [dbt-cloud job export](#dbt-cloud-job-export)
* [dbt-cloud job import](#dbt-cloud-job-import)
* [dbt-cloud run get](#dbt-cloud-run-get)
* [dbt-cloud run cancel](#dbt-cloud-run-cancel)
* [dbt-cloud run cancel-all](#dbt-cloud-run-cancel-all)
* [dbt-cloud run list](#dbt-cloud-run-list)
* [dbt-cloud run list-artifacts](#dbt-cloud-run-list-artifacts)
* [dbt-cloud run get-artifact](#dbt-cloud-run-get-artifact)
* [dbt-cloud metadata query](#dbt-cloud-metadata-query)

## dbt-cloud account get
This command retrieves dbt Cloud account information. For more information on the API endpoint arguments and response, run `dbt-cloud account get --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#tag/Accounts/operation/getAccountById).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud account get
{
    "status": {
        "code": 200,
        "is_success": true,
        "user_message": "Success!",
        "developer_message": ""
    },
    "data": {
        "docs_job_id": null,
        "freshness_job_id": null,
        "lock_reason": null,
        "unlock_if_subscription_renewed": false,
        "read_only_seats": 10,
        "id": 1,
        "name": "REDACTED",
        "state": 1,
        "plan": "enterprise",
        "pending_cancel": false,
        "run_slots": 15,
        "developer_seats": 10,
        "queue_limit": 50,
        "pod_memory_request_mebibytes": 600,
        "run_duration_limit_seconds": 86400,
        "enterprise_authentication_method": null,
        "enterprise_login_slug": null,
        "enterprise_unique_identifier": null,
        "billing_email_address": null,
        "locked": false,
        "develop_file_system": true,
        "unlocked_at": null,
        "created_at": "2021-04-14T20:23:00.305964+00:00",
        "updated_at": "2022-05-17T16:45:23.288391+00:00",
        "starter_repo_url": null,
        "sso_reauth": false,
        "git_auth_level": "personal",
        "identifier": "REDACTED",
        "docs_job": null,
        "freshness_job": null,
        "enterprise_login_url": "https://cloud.getdbt.com/enterprise-login/None/"
    }
}
```
</details>

## dbt-cloud account list
This command retrieves all available dbt Cloud accounts. For more information on the API endpoint arguments and response, run `dbt-cloud account list --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listAccounts).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud account list
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    {
      "docs_job_id": null,
      "freshness_job_id": null,
      "lock_reason": null,
      "unlock_if_subscription_renewed": false,
      "read_only_seats": 50,
      "id": REDACTED,
      "name": "Jaffle Shop",
      "state": 1,
      "plan": "team",
      "pending_cancel": false,
      "run_slots": 5,
      "developer_seats": 4,
      "queue_limit": 50,
      "pod_memory_request_mebibytes": 600,
      "run_duration_limit_seconds": 86400,
      "enterprise_authentication_method": null,
      "enterprise_login_slug": null,
      "enterprise_unique_identifier": null,
      "billing_email_address": "REDACTED",
      "locked": false,
      "develop_file_system": true,
      "unlocked_at": null,
      "created_at": "2021-09-06T07:41:12.146234+00:00",
      "updated_at": "2022-03-07T06:05:33.350381+00:00",
      "starter_repo_url": null,
      "sso_reauth": false,
      "git_auth_level": "team",
      "identifier": "REDACTED",
      "docs_job": null,
      "freshness_job": null,
      "enterprise_login_url": "https://cloud.getdbt.com/enterprise-login/None/"
    }
  ],
  "extra": {
    "filters": {
      "pk__in": [
        REDACTED
      ]
    },
    "order_by": null,
    "pagination": {
      "count": 1,
      "total_count": 1
    }
  }
}
```
</details>

## dbt-cloud audit-log get

❗ **This command is available for Enterprise accounts only.**

This command retrieves audit logs for the dbt Cloud account. For more information on the command, run `dbt-cloud audit-log get --help`. This command uses the API v3 which has no official documentation yet.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud audit-log get --logged-at-start 2022-05-01 --logged-at-end 2022-05-07 --limit 1
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    {
      "account_id": 123456,
      "service": "SERVICE_DBT_CLOUD",
      "source": "SOURCE_CLOUD_UI",
      "routing_key": "v1.events.auth.credentialsloginsucceeded",
      "actor_type": "ACTOR_USER",
      "actor_name": "REDACTED",
      "actor_id": 123454,
      "logged_at": "2022-05-05 06:51:10+00:00",
      "uuid": "8868c439-8928-4e8c-924b-77558d65db0b",
      "actor_ip": "REDACTED",
      "metadata": {
        "auth_credentials": {
          "user": {
            "id": "REDACTED",
            "email": "REDACTED"
          }
        }
      },
      "internal": false,
      "id": 1809583,
      "state": 1,
      "created_at": "2022-05-05 06:51:12.454677+00:00",
      "updated_at": "2022-05-05 06:51:12.454677+00:00"
    }
  ],
  "extra": {
    "filters": {
      "account_id": 123456,
      "limit": 1,
      "offset": 0,
      "logged_at__range": [
        "2022-05-01 00:00:00Z",
        "2022-05-07 00:00:00Z"
      ],
      "internal": false
    },
    "order_by": "-logged_at",
    "pagination": {
      "count": 1,
      "total_count": 4
    }
  }
}
```
</details>

## dbt-cloud project get
This command retrieves dbt Cloud project information. For more information on the API endpoint arguments and response, run `dbt-cloud project get --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#tag/Projects/operation/getProjectById).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud project get
```

[Click to view sample response](tests/data/project_get_response.json)
</details>


## dbt-cloud project list
This command returns a list of projects in the account. For more information on the API endpoint arguments and response, run `dbt-cloud project list --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listProjects).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud project list
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    {
      "name": "jaffle_shop",
      "account_id": REDACTED,
      "repository_id": REDACTED,
      "connection_id": REDACTED,
      "id": REDACTED,
      "created_at": "2021-04-14 20:23:00.395285+00:00",
      "updated_at": "2021-11-16 16:32:43.960836+00:00",
      "skipped_setup": false,
      "state": 1,
      "dbt_project_subdirectory": null,
      "connection": {
        "id": REDACTED,
        "account_id": REDACTED,
        "project_id": REDACTED,
        "name": "Bigquery",
        "type": "bigquery",
        "created_by_id": REDACTED,
        "created_by_service_token_id": null,
        "details": {
          "project_id": "REDACTED",
          "timeout_seconds": 300,
          "private_key_id": "REDACTED",
          "client_email": "REDACTED",
          "client_id": "REDACTED",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "REDACTED",
          "retries": 1,
          "location": null,
          "is_configured_for_oauth": false
        },
        "state": 1,
        "created_at": "2021-11-16 16:26:01.571115+00:00",
        "updated_at": "2021-11-16 16:37:42.500015+00:00"
      },
      "repository": {
        "id": REDACTED,
        "account_id": REDACTED,
        "project_id": REDACTED,
        "full_name": "REDACTED",
        "remote_url": "REDACTED",
        "remote_backend": "github",
        "git_clone_strategy": "github_app",
        "deploy_key_id": REDACTED,
        "repository_credentials_id": null,
        "github_installation_id": REDACTED,
        "pull_request_url_template": "REDACTED",
        "state": 1,
        "created_at": "2021-11-16 16:26:24.412439+00:00",
        "updated_at": "2021-11-16 16:26:24.412455+00:00",
        "deploy_key": {
          "id": REDACTED,
          "account_id": REDACTED,
          "state": 1,
          "public_key": "REDACTED"
        },
        "github_repo": "REDACTED",
        "name": "jaffle_shop",
        "git_provider_id": REDACTED,
        "gitlab": null,
        "git_provider": null
      },
      "group_permissions": [],
      "docs_job_id": null,
      "freshness_job_id": null,
      "docs_job": null,
      "freshness_job": null
    }
  ],
  "extra": {
    "filters": {
      "account_id": REDACTED,
      "limit": 100,
      "offset": 0
    },
    "order_by": "id",
    "pagination": {
      "count": 1,
      "total_count": 1
    }
  }
}
```
</details>

## dbt-cloud environment list
This command retrieves environments for a given project. For more information on the command, run `dbt-cloud environment list --help`. This command uses the API v3 which has no official documentation yet.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud environment list
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    {
      "id": REDACTED,
      "account_id": REDACTED,
      "project_id": REDACTED,
      "credentials_id": null,
      "name": "Development",
      "dbt_version": "0.21.0",
      "type": "development",
      "use_custom_branch": false,
      "custom_branch": null,
      "supports_docs": false,
      "state": 1,
      "created_at": "2021-11-16 16:26:02.542507+00:00",
      "updated_at": "2021-11-16 16:26:02.542525+00:00",
      "project": {
        "name": "jaffle_shop",
        "account_id": REDACTED,
        "repository_id": REDACTED,
        "connection_id": REDACTED,
        "id": REDACTED,
        "created_at": "2021-04-14 20:23:00.395285+00:00",
        "updated_at": "2021-11-16 16:32:43.960836+00:00",
        "skipped_setup": false,
        "state": 1,
        "dbt_project_subdirectory": null,
        "connection": {
          "id": REDACTED,
          "account_id": REDACTED,
          "project_id": REDACTED,
          "name": "Bigquery",
          "type": "bigquery",
          "created_by_id": REDACTED,
          "created_by_service_token_id": null,
          "details": {
            "project_id": "REDACTED",
            "timeout_seconds": 300,
            "private_key_id": "REDACTED",
            "client_email": "REDACTED",
            "client_id": "REDACTED",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "REDACTED",
            "retries": 1,
            "location": null,
            "maximum_bytes_billed": null,
            "is_configured_for_oauth": false
          },
          "state": 1,
          "created_at": "2021-11-16 16:26:01.571115+00:00",
          "updated_at": "2021-11-16 16:37:42.500015+00:00"
        },
        "repository": {
          "id": REDACTED,
          "account_id": REDACTED,
          "project_id": REDACTED,
          "full_name": "REDACTED",
          "remote_url": "REDACTED",
          "remote_backend": "github",
          "git_clone_strategy": "github_app",
          "deploy_key_id": REDACTED,
          "repository_credentials_id": null,
          "github_installation_id": REDACTED,
          "pull_request_url_template": "REDACTED",
          "state": 1,
          "created_at": "2021-11-16 16:26:24.412439+00:00",
          "updated_at": "2021-11-16 16:26:24.412455+00:00",
          "deploy_key": {
            "id": REDACTED,
            "account_id": REDACTED,
            "state": 1,
            "public_key": "REDACTED"
          },
          "github_repo": "REDACTED",
          "name": "jaffle_shop",
          "git_provider_id": REDACTED,
          "gitlab": null,
          "git_provider": null
        },
        "group_permissions": null,
        "docs_job_id": null,
        "freshness_job_id": null,
        "docs_job": null,
        "freshness_job": null
      },
      "jobs": null,
      "credentials": null,
      "custom_environment_variables": null
    }
  ],
  "extra": {
    "filters": {
      "account_id": REDACTED,
      "project_id": REDACTED,
      "limit": 100,
      "offset": 0
    },
    "order_by": "id",
    "pagination": {
      "count": 2,
      "total_count": 2
    }
  }
}
```
</details>

## dbt-cloud job run
This command triggers a dbt Cloud job run and returns a run status JSON response. For more information on the API endpoint arguments and response, run `dbt-cloud job run --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/triggerRun).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job run --job-id 43167 --cause "My first run!" --steps-override '["dbt seed", "dbt run"]' --wait
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
</details>

## dbt-cloud job get
This command returns the details of a dbt Cloud job. For more information on the API endpoint arguments and response, run `dbt-cloud job get --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getJobById).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job get --job-id 43167
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "execution": {
      "timeout_seconds": 0
    },
    "generate_docs": false,
    "run_generate_sources": false,
    "id": 43167,
    "account_id": REDACTED,
    "project_id": REDACTED,
    "environment_id": 49819,
    "name": "Do nothing!",
    "dbt_version": null,
    "created_at": "2021-11-18T15:19:03.185668+00:00",
    "updated_at": "2021-11-18T15:19:03.185687+00:00",
    "execute_steps": [
      "dbt run -s not_a_model"
    ],
    "state": 1,
    "deferring_job_definition_id": null,
    "lifecycle_webhooks": false,
    "lifecycle_webhooks_url": null,
    "triggers": {
      "github_webhook": false,
      "git_provider_webhook": false,
      "custom_branch_only": true,
      "schedule": false
    },
    "settings": {
      "threads": 4,
      "target_name": "default"
    },
    "schedule": {
      "cron": "0 * * * *",
      "date": {
        "type": "every_day"
      },
      "time": {
        "type": "every_hour",
        "interval": 1
      }
    },
    "is_deferrable": false,
    "generate_sources": false,
    "cron_humanized": "Every hour",
    "next_run": null,
    "next_run_humanized": null
  }
}
```
</details>

## dbt-cloud job list
This command returns a list of jobs in the account. For more information on the API endpoint arguments and response, run `dbt-cloud job list --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listJobsForAccount).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job list
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    {
      "execution": {
        "timeout_seconds": 0
      },
      "generate_docs": false,
      "run_generate_sources": false,
      "id": 43167,
      "account_id": REDACTED,
      "project_id": REDACTED,
      "environment_id": 49819,
      "name": "Do nothing!",
      "dbt_version": null,
      "created_at": "2021-11-18T15:19:03.185668+00:00",
      "updated_at": "2021-12-25T09:17:12.788186+00:00",
      "execute_steps": [
        "dbt run -s not_a_model"
      ],
      "state": 1,
      "deferring_job_definition_id": null,
      "lifecycle_webhooks": false,
      "lifecycle_webhooks_url": null,
      "triggers": {
        "github_webhook": false,
        "git_provider_webhook": null,
        "custom_branch_only": true,
        "schedule": false
      },
      "settings": {
        "threads": 4,
        "target_name": "default"
      },
      "schedule": {
        "cron": "0 * * * *",
        "date": {
          "type": "every_day"
        },
        "time": {
          "type": "every_hour",
          "interval": 1
        }
      },
      "is_deferrable": false,
      "generate_sources": false,
      "cron_humanized": "Every hour",
      "next_run": null,
      "next_run_humanized": null
    }
  ]
}
```
</details>

## dbt-cloud job create

This command creates a job in a dbt Cloud project. For more information on the API endpoint arguments and response, run `dbt-cloud job create --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/createJob).

<details>
  <summary><b>Usage</b></summary>

```bash
dbt-cloud job create --project-id 12345 --environment-id 49819 --name "Create job" --execute-steps '["dbt seed", "dbt run"]'
{
  "status": {
    "code": 201,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "execution": {
      "timeout_seconds": 0
    },
    "generate_docs": false,
    "run_generate_sources": false,
    "id": 48180,
    "account_id": REDACTED,
    "project_id": 12345,
    "environment_id": 49819,
    "name": "Create job",
    "dbt_version": null,
    "created_at": "2021-12-22T11:23:26.968076+00:00",
    "updated_at": "2021-12-22T11:23:26.968094+00:00",
    "execute_steps": [
      "dbt seed",
      "dbt run"
    ],
    "state": 1,
    "deferring_job_definition_id": null,
    "lifecycle_webhooks": false,
    "lifecycle_webhooks_url": null,
    "triggers": {
      "github_webhook": false,
      "git_provider_webhook": null,
      "custom_branch_only": false,
      "schedule": false
    },
    "settings": {
      "threads": 1,
      "target_name": "default"
    },
    "schedule": {
      "cron": "0 * * * *",
      "date": {
        "type": "every_day"
      },
      "time": {
        "type": "every_hour",
        "interval": 1
      }
    },
    "is_deferrable": false,
    "generate_sources": false,
    "cron_humanized": "Every hour",
    "next_run": null,
    "next_run_humanized": null
  }
}
```
</details>

## dbt-cloud job delete

This command deletes a job in a dbt Cloud project. Note that this command uses an undocumented v3 API endpoint. For more information on the command and its arguments, run `dbt-cloud job delete --help`.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job delete --job-id 48474
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "execution": {
      "timeout_seconds": 0
    },
    "generate_docs": false,
    "run_generate_sources": false,
    "id": 48474,
    "account_id": REDACTED,
    "project_id": REDACTED,
    "environment_id": 49819,
    "name": "Do nothing!",
    "dbt_version": null,
    "created_at": "2021-12-25T10:12:29.114456+00:00",
    "updated_at": "2021-12-25T10:12:29.814383+00:00",
    "execute_steps": [
      "dbt run -s not_a_model"
    ],
    "state": 2,
    "deferring_job_definition_id": null,
    "lifecycle_webhooks": false,
    "lifecycle_webhooks_url": null,
    "triggers": {
      "github_webhook": false,
      "git_provider_webhook": null,
      "custom_branch_only": true,
      "schedule": false
    },
    "settings": {
      "threads": 4,
      "target_name": "default"
    },
    "schedule": {
      "cron": "0 * * * *",
      "date": {
        "type": "every_day"
      },
      "time": {
        "type": "every_hour",
        "interval": 1
      }
    },
    "is_deferrable": false,
    "generate_sources": false,
    "cron_humanized": "Every hour",
    "next_run": null,
    "next_run_humanized": null
  }
}
```
</details>

## dbt-cloud job delete-all

💡 **This command is a composition of one or more base commands.**

This command fetches all jobs on the account, deletes them one-by-one after user confirmation via prompt and prints out the job delete responses. For more information on the command and its arguments, run `dbt-cloud job delete-all --help`.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job delete-all --keep-jobs "[43167, 49663]"
Jobs to delete: [54658, 54659]
Delete job 54658? [y/N]: yes
Job 54658 was deleted.
Delete job 54659? [y/N]: yes
Job 54659 was deleted.
[
  {
    "status": {
      "code": 200,
      "is_success": true,
      "user_message": "Success!",
      "developer_message": ""
    },
    "data": {
      "execution": {
        "timeout_seconds": 0
      },
      "generate_docs": false,
      "run_generate_sources": false,
      "id": 54658,
      "account_id": REDACTED,
      "project_id": REDACTED,
      "environment_id": 49819,
      "name": "Do nothing!",
      "dbt_version": null,
      "created_at": "2022-01-27T09:04:26.080595+00:00",
      "updated_at": "2022-01-27T09:05:10.527583+00:00",
      "execute_steps": [
        "dbt run -s not_a_model"
      ],
      "state": 2,
      "deferring_job_definition_id": null,
      "lifecycle_webhooks": false,
      "lifecycle_webhooks_url": null,
      "triggers": {
        "github_webhook": false,
        "git_provider_webhook": null,
        "custom_branch_only": true,
        "schedule": false
      },
      "settings": {
        "threads": 4,
        "target_name": "default"
      },
      "schedule": {
        "cron": "0 * * * *",
        "date": {
          "type": "every_day"
        },
        "time": {
          "type": "every_hour",
          "interval": 1
        }
      },
      "is_deferrable": false,
      "generate_sources": false,
      "cron_humanized": "Every hour",
      "next_run": null,
      "next_run_humanized": null
    }
  },
  {
    "status": {
      "code": 200,
      "is_success": true,
      "user_message": "Success!",
      "developer_message": ""
    },
    "data": {
      "execution": {
        "timeout_seconds": 0
      },
      "generate_docs": false,
      "run_generate_sources": false,
      "id": 54659,
      "account_id": REDACTED,
      "project_id": REDACTED,
      "environment_id": 49819,
      "name": "Do nothing!",
      "dbt_version": null,
      "created_at": "2022-01-27T09:04:43.231873+00:00",
      "updated_at": "2022-01-27T09:05:19.533456+00:00",
      "execute_steps": [
        "dbt run -s not_a_model"
      ],
      "state": 2,
      "deferring_job_definition_id": null,
      "lifecycle_webhooks": false,
      "lifecycle_webhooks_url": null,
      "triggers": {
        "github_webhook": false,
        "git_provider_webhook": null,
        "custom_branch_only": true,
        "schedule": false
      },
      "settings": {
        "threads": 4,
        "target_name": "default"
      },
      "schedule": {
        "cron": "0 * * * *",
        "date": {
          "type": "every_day"
        },
        "time": {
          "type": "every_hour",
          "interval": 1
        }
      },
      "is_deferrable": false,
      "generate_sources": false,
      "cron_humanized": "Every hour",
      "next_run": null,
      "next_run_humanized": null
    }
  }
]
```
</details>

## dbt-cloud job export

💡 **This command is a composition of one or more base commands.**

This command exports a dbt Cloud job as JSON to a file and can be used in conjunction with [dbt-cloud job import](#dbt-cloud-job-import) to copy jobs between dbt Cloud projects.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud job export | tee job.json
{
  "execution": {
    "timeout_seconds": 0
  },
  "generate_docs": false,
  "run_generate_sources": false,
  "account_id": REDACTED,
  "project_id": REDACTED,
  "environment_id": 49819,
  "name": "Do nothing!",
  "dbt_version": null,
  "created_at": "2021-11-18T15:19:03.185668+00:00",
  "updated_at": "2021-12-25T09:17:12.788186+00:00",
  "execute_steps": [
    "dbt run -s not_a_model"
  ],
  "state": 1,
  "deferring_job_definition_id": null,
  "lifecycle_webhooks": false,
  "lifecycle_webhooks_url": null,
  "triggers": {
    "github_webhook": false,
    "git_provider_webhook": null,
    "custom_branch_only": true,
    "schedule": false
  },
  "settings": {
    "threads": 4,
    "target_name": "default"
  },
  "schedule": {
    "cron": "0 * * * *",
    "date": {
      "type": "every_day"
    },
    "time": {
      "type": "every_hour",
      "interval": 1
    }
  },
  "is_deferrable": false,
  "generate_sources": false,
  "cron_humanized": "Every hour",
  "next_run": null,
  "next_run_humanized": null
}
```
</details>

## dbt-cloud job import

💡 **This command is a composition of one or more base commands.**

This command imports a dbt Cloud job from exported JSON. You can use JSON manipulation tools (e.g., [jq](https://stedolan.github.io/jq/)) to modify the job definition before importing it.

<details>
  <summary><b>Usage</b></summary>

```bash
>> cat job.json | jq '.environment_id = 49819 | .name = "Imported job"' | dbt-cloud job import
{
  "status": {
    "code": 201,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "execution": {
      "timeout_seconds": 0
    },
    "generate_docs": false,
    "run_generate_sources": false,
    "id": 48475,
    "account_id": REDACTED,
    "project_id": REDACTED,
    "environment_id": 49819,
    "name": "Imported job",
    "dbt_version": null,
    "created_at": "2021-12-25T10:40:13.193129+00:00",
    "updated_at": "2021-12-25T10:40:13.193149+00:00",
    "execute_steps": [
      "dbt run -s not_a_model"
    ],
    "state": 1,
    "deferring_job_definition_id": null,
    "lifecycle_webhooks": false,
    "lifecycle_webhooks_url": null,
    "triggers": {
      "github_webhook": false,
      "git_provider_webhook": null,
      "custom_branch_only": true,
      "schedule": false
    },
    "settings": {
      "threads": 4,
      "target_name": "default"
    },
    "schedule": {
      "cron": "0 * * * *",
      "date": {
        "type": "every_day"
      },
      "time": {
        "type": "every_hour",
        "interval": 1
      }
    },
    "is_deferrable": false,
    "generate_sources": false,
    "cron_humanized": "Every hour",
    "next_run": null,
    "next_run_humanized": null
  }
}
```
</details>

## dbt-cloud run get
This command returns the details of a dbt Cloud run. For more information on the API endpoint arguments and response, run `dbt-cloud run get --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getRunById).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run get --run-id 36053848
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
    "created_at_humanized": "2 weeks, 1 day ago",
    "finished_at_humanized": "2 weeks, 1 day ago",
    "job_id": 43167
  }
}
```
</details>

## dbt-cloud run list
This command returns a list of runs in the account. For more information on the API endpoint arguments and response, run `dbt-cloud run list --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#tag/Runs/operation/listRunsForAccount).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run list --limit 2
{
  "data": [
    {
      "id": "40650768",
      "environment_id": "49819",
      "account_id": REDACTED,
      "project_id": REDACTED,
      "job_id": "49663",
      "trigger": {
        "cause": "scheduled",
        "git_provider": null,
        "pull_request_id": null,
        "git_branch": "main",
        "git_sha": "981c5cf1ba299e942c6c277c38c8dec9b0738dd0"
      },
      "replace": {
        "schema_with": null,
        "target_name_with": null,
        "dbt_version_with": null,
        "generate_docs_with": null,
        "run_steps_with": null,
        "thread_count_with": null,
        "timeout_after_with": null
      },
      "href": "https://cloud.getdbt.com/api/v2/accounts/REDACTED/runs/40650768",
      "status": "Succeeded",
      "status_message": null,
      "dbt_version": "0.21.0",
      "waiting_on": [],
      "triggered_at": 1642377765,
      "created_at": 1642377765,
      "updated_at": 1642378181,
      "dequeued_at": 1642377904,
      "started_at": 1642378141,
      "finished_at": 1642378181,
      "duration": 416,
      "queued_duration": 376,
      "run_duration": 40,
      "artifacts_saved": true,
      "has_docs_generated": true,
      "has_sources_generated": false
    },
    {
      "id": "40538548",
      "environment_id": "49819",
      "account_id": REDACTED,
      "project_id": REDACTED,
      "job_id": "49663",
      "trigger": {
        "cause": "scheduled",
        "git_provider": null,
        "pull_request_id": null,
        "git_branch": "main",
        "git_sha": "981c5cf1ba299e942c6c277c38c8dec9b0738dd0"
      },
      "replace": {
        "schema_with": null,
        "target_name_with": null,
        "dbt_version_with": null,
        "generate_docs_with": null,
        "run_steps_with": null,
        "thread_count_with": null,
        "timeout_after_with": null
      },
      "href": "https://cloud.getdbt.com/api/v2/accounts/REDACTED/runs/40538548",
      "status": "Succeeded",
      "status_message": null,
      "dbt_version": "0.21.0",
      "waiting_on": [],
      "triggered_at": 1642291308,
      "created_at": 1642291308,
      "updated_at": 1642291725,
      "dequeued_at": 1642291455,
      "started_at": 1642291683,
      "finished_at": 1642291725,
      "duration": 417,
      "queued_duration": 375,
      "run_duration": 42,
      "artifacts_saved": true,
      "has_docs_generated": true,
      "has_sources_generated": false
    }
  ]
}
```
</details>

## dbt-cloud run cancel
This command cancels a dbt Cloud run. For more information on the API endpoint arguments and response, run `dbt-cloud run cancel --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/cancelRunById).

> A run can be to be 'cancelled' irregardless of it's previous status. This means that you can send a request to cancel a previously successful / errored run (and nothing happens practically) and the response status would be similar to
> cancelling a currently queued or running run.

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run cancel --run-id 36053848
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": {
    "id": 36053848,
    "trigger_id": 48392125,
    "account_id": 123456,
    "environment_id": 49819,
    "project_id": 123457,
    "job_definition_id": 37119,
    "status": 30,
    "dbt_version": "0.19.1",
    "git_branch": null,
    "git_sha": null,
    "status_message": "Cancelled by user.",
    "owner_thread_id": null,
    "executed_by_thread_id": null,
    "deferring_run_id": null,
    "artifacts_saved": false,
    "artifact_s3_path": null,
    "has_docs_generated": false,
    "has_sources_generated": false,
    "notifications_sent": false,
    "blocked_by": [],
    "scribe_enabled": true,
    "created_at": "2022-03-14 09:58:13.138036+00:00",
    "updated_at": "2022-03-14 09:58:22.869828+00:00",
    "dequeued_at": null,
    "started_at": null,
    "finished_at": "2022-03-14 09:58:22.867735+00:00",
    "last_checked_at": null,
    "last_heartbeat_at": null,
    "should_start_at": null,
    "trigger": null,
    "job": null,
    "environment": null,
    "run_steps": [],
    "status_humanized": "Cancelled",
    "in_progress": false,
    "is_complete": true,
    "is_success": false,
    "is_error": false,
    "is_cancelled": true,
    "href": "REDACTED",
    "duration": "00:00:09",
    "queued_duration": "00:00:09",
    "run_duration": "00:00:00",
    "duration_humanized": "9 seconds",
    "queued_duration_humanized": "9 seconds",
    "run_duration_humanized": "0 minutes",
    "created_at_humanized": "9 seconds ago",
    "finished_at_humanized": "0 minutes ago",
    "job_id": 43167
  }
}
```
</details>

## dbt-cloud run cancel-all

💡 **This command is a composition of one or more base commands.**

This command fetches all runs on the account, cancels them one-by-one after user confirmation via prompt and prints out the run cancellation responses. For more information on the command and its arguments, run `dbt-cloud run cancel-all --help`.

> You should typically use this with a `--status` arg of either `Running` or `Queued` as cancellations can be requested against all runs. Without this, you will effectively be trying to cancel all runs that had ever been scheduled in the project irregardless of its' current status (which could take a long time if your project has had a lot of previous runs).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run cancel-all --status Running
Runs to cancel: [36053848]
Cancel run 36053848? [y/N]: yes
Run 36053848 has been cancelled.
[
  {
    "status": {
      "code": 200,
      "is_success": true,
      "user_message": "Success!",
      "developer_message": ""
    },
    "data": {
      "id": 36053848,
      "trigger_id": 48392125,
      "account_id": 123456,
      "environment_id": 49819,
      "project_id": 123457,
      "job_definition_id": 37119,
      "status": 30,
      "dbt_version": "0.19.1",
      "git_branch": null,
      "git_sha": null,
      "status_message": "Cancelled by user.",
      "owner_thread_id": null,
      "executed_by_thread_id": null,
      "deferring_run_id": null,
      "artifacts_saved": false,
      "artifact_s3_path": null,
      "has_docs_generated": false,
      "has_sources_generated": false,
      "notifications_sent": false,
      "blocked_by": [],
      "scribe_enabled": true,
      "created_at": "2022-03-14 09:58:13.138036+00:00",
      "updated_at": "2022-03-14 09:58:22.869828+00:00",
      "dequeued_at": null,
      "started_at": null,
      "finished_at": "2022-03-14 09:58:22.867735+00:00",
      "last_checked_at": null,
      "last_heartbeat_at": null,
      "should_start_at": null,
      "trigger": null,
      "job": null,
      "environment": null,
      "run_steps": [],
      "status_humanized": "Cancelled",
      "in_progress": false,
      "is_complete": true,
      "is_success": false,
      "is_error": false,
      "is_cancelled": true,
      "href": "REDACTED",
      "duration": "00:00:09",
      "queued_duration": "00:00:09",
      "run_duration": "00:00:00",
      "duration_humanized": "9 seconds",
      "queued_duration_humanized": "9 seconds",
      "run_duration_humanized": "0 minutes",
      "created_at_humanized": "9 seconds ago",
      "finished_at_humanized": "0 minutes ago",
      "job_id": 43167
    }
  }
]
```
</details>

## dbt-cloud run list-artifacts
This command fetches a list of artifact files generated for a completed run. For more information on the API endpoint arguments and response, run `dbt-cloud run list-artifacts --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/listArtifactsByRunId).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run list-artifacts --run-id 36053848
{
  "status": {
    "code": 200,
    "is_success": true,
    "user_message": "Success!",
    "developer_message": ""
  },
  "data": [
    "manifest.json",
    "run/jaffle_shop/data/raw_customers.csv",
    "run/jaffle_shop/data/raw_orders.csv",
    "run/jaffle_shop/data/raw_payments.csv",
    "run_results.json"
  ]
}
```
</details>

## dbt-cloud run get-artifact
This command fetches an artifact file from a completed run. Once a run has completed, you can use this command to download the manifest.json, run_results.json or catalog.json files from dbt Cloud. These artifacts contain information about the models in your dbt project, timing information around their execution, and a status message indicating the result of the model build.

For more information on the API endpoint arguments and response, run `dbt-cloud run get-artifact --help` and check out the [dbt Cloud API docs](https://docs.getdbt.com/dbt-cloud/api-v2#operation/getArtifactsByRunId).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud run get-artifact --run-id 36053848 --path manifest.json > manifest.json
```
</details>

## dbt-cloud metadata query
This command queries the dbt Cloud Metadata API using GraphQL. For more information on the Metadata API, see [the docs](https://docs.getdbt.com/docs/dbt-cloud/dbt-cloud-api/metadata/metadata-overview).

<details>
  <summary><b>Usage</b></summary>

```bash
>> dbt-cloud metadata query -f query.graphql
{
  "data": {
    "model": {
      "parentsModels": [
        {
          "runId": 39352464,
          "uniqueId": "model.jaffle_shop.stg_orders",
          "executionTime": 0.870538949966431
        },
        {
          "runId": 39352464,
          "uniqueId": "model.jaffle_shop.stg_payments",
          "executionTime": 0.635890483856201
        },
        {
          "runId": 39352464,
          "uniqueId": "model.jaffle_shop.stg_customers",
          "executionTime": 0.697099924087524
        }
      ],
      "parentsSources": []
    }
  }
}
```

```graphql
""" query.graphql """
{
  model(jobId: 49663, uniqueId: "model.jaffle_shop.customers") {
    parentsModels {
      runId
      uniqueId
      executionTime
    }
    parentsSources {
      runId
      uniqueId
      state
    }
  }
}
```

An alternative way of using the command without saving the GraphQL query to a file is to pipe it to `dbt-cloud metadata query`.
```bash
>> echo '{
  model(jobId: 49663, uniqueId: "model.jaffle_shop.customers") {
    parentsModels {
      runId
      uniqueId
      executionTime
    }
    parentsSources {
      runId
      uniqueId
      state
    }
  }
}' | dbt-cloud metadata query
```

</details>

# Demo utilities

The utilities listed here are for demonstration purposes only and are subject to change. In order to use the demo utilities you need to install the `dbt-cloud-cli` with extra `demo` dependencies:

```bash
pip install dbt-cloud-cli[demo]
```

## dbt-cloud demo data-catalog

An interactive CLI application for exploring `catalog.json` artifacts.

<details>
  <summary><b>Usage</b></summary>

```bash
>> latest_run_id=$(dbt-cloud run list --job-id $DBT_CLOUD_JOB_ID --limit 1 | jq .data[0].id -r)
>> dbt-cloud run get-artifact --run-id $latest_run_id --path catalog.json -f catalog.json
>> dbt-cloud demo data-catalog -f catalog.json



  #####           ##              ###           ##           ##               
  ##  ##          ##             ## ##          ##           ##               
 ##   ##   ###  #####   ###     ##  ##   ###  #####   ###   ##    ###    #### 
 ##   ##  #  ##  ##    #  ##    ##      #  ##  ##    #  ##  ##   ## ##  ## ## 
 ##  ##    ####  ##     ####   ##        ####  ##     ####  ##  ##  ##  #  ## 
##   ##  ## ##  ##    ## ##    ##   #  ## ##  ##    ## ##  ##   ##  ## ##  #  
##  ##   ## ##  ##    ## ##    ##  ##  ## ##  ##    ## ##  ##   ## ##  ## ##  
#####     ## ##  ##    ## ##    ####    ## ##  ##    ## ## ##    ###    ####  
                                                                         ##   
                                                                       ###    

[?] Select node type to explore: source
 > source
   node
```
</details>

## Acknowledgements

Thanks to [Sean McIntyre](https://github.com/boxysean) for his initial work on triggering a dbt Cloud job using Python as proposed in [this post on dbt Discourse](https://discourse.getdbt.com/t/triggering-a-dbt-cloud-job-in-your-automated-workflow-with-python/2573). Thank you for sharing your work with the community!
