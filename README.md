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

# Commands

For more information on a command, run `dbt-cloud <command> --help`. For more information on the API endpoints, see [dbt Cloud API V3 docs](https://docs.getdbt.com/dbt-cloud/api-v3) and [dbt Cloud Metadata API docs](https://docs.getdbt.com/docs/dbt-cloud/dbt-cloud-api/metadata/metadata-overview).


| Group        | Command                                               | Implemented | API endpoint                                        |
| ------------ | ----------------------------------------------------- | -------------------------------------------------- | ----------- | 
| Account      | [dbt-cloud account get](#dbt-cloud-account-get)       | ✅           | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/`                   | 
| Account      | [dbt-cloud account list](#dbt-cloud-account-list)     | ✅           | GET `https://{dbt_cloud_host}/api/v3/accounts/`                                | 
| Audit log    | [dbt-cloud audit-log get](#dbt-cloud-audit-log-get)   | ✅           | GET `https://{dbt_cloud_host}/api/v3/audit-logs/`                              | 
| Project      | [dbt-cloud project create](#dbt-cloud-project-create) | ✅           | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/`         | 
| Project      | [dbt-cloud project delete](#dbt-cloud-project-delete) | ✅           | DELETE `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{id}/`  |
| Project      | [dbt-cloud project get](#dbt-cloud-project-get)       | ✅           | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{id}/`     | 
| Project      | [dbt-cloud project list](#dbt-cloud-project-list)     | ✅           | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/`          |  
| Project      | [dbt-cloud project update](#dbt-cloud-project-update) | ✅           | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{id}/`     | 
| Environment  | [dbt-cloud environment create](#dbt-cloud-environment-create) | ✅          | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/environments/` | 
| Environment  | [dbt-cloud environment delete](#dbt-cloud-environment-delete) | ✅ | DELETE `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/environments/{id}/` |  
| Environment  | [dbt-cloud environment get](#dbt-cloud-environment-get) | ✅ | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/environments/{id}/` |  
| Environment  | [dbt-cloud environment list](#dbt-cloud-environment-list) | ✅ | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/environments/` |  
| Environment  | [dbt-cloud environment update](#dbt-cloud-environment-update) | ❌ | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/environments/{id}/` |  
| Connection  | [dbt-cloud connection create](#dbt-cloud-connection-create) | ✅ | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{project_id}/connections/` | 
| Connection  | [dbt-cloud connection delete](#dbt-cloud-connection-delete) | ✅ | DELETE `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{project_id}/connections/{id}/` | 
| Connection  | [dbt-cloud connection get](#dbt-cloud-connection-get) | ✅ | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{project_id}/connections/{id}/` | 
| Connection  | [dbt-cloud connection list](#dbt-cloud-connection-list) | ✅ | GET `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{project_id}/connections/` | 
| Connection  | [dbt-cloud connection update](#dbt-cloud-connection-update) | ❌ | POST `https://{dbt_cloud_host}/api/v3/accounts/{account_id}/projects/{project_id}/connections/{id}/` | 
| Repository  | [dbt-cloud repository create](#dbt-cloud-repository-create) | ❌ | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/repositories/` | 
| Repository  | [dbt-cloud repository delete](#dbt-cloud-repository-delete) | ❌ | DELETE `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/repositories/{id}/` | 
| Repository  | [dbt-cloud repository get](#dbt-cloud-repository-get) | ❌ | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/repositories/{id}/` | 
| Repository  | [dbt-cloud repository list](#dbt-cloud-repository-list) | ❌ | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/repositories/` | 
| Job          | [dbt-cloud job create](#dbt-cloud-job-create)         | ✅          | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/                              `                      |  
| Job          | [dbt-cloud job delete](#dbt-cloud-job-delete)         | ✅          | DELETE `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/{id}/`                                                    | 
| Job          | [dbt-cloud job delete-all](#dbt-cloud-job-delete-all) |  ✅          | Uses a composition of one or more endpoints                                                 | 
| Job          | [dbt-cloud job get](#dbt-cloud-job-get)               | ✅          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/{id}/`                                                    | 
| Job          | [dbt-cloud job list](#dbt-cloud-job-list)             | ✅          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/`                                                    |  
| Job          | [dbt-cloud job run](#dbt-cloud-job-run)               | ✅          | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/{job_id}/run/`                                                    |  
| Job          | [dbt-cloud job update](#dbt-cloud-job-update)         | ❌          | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/{id}/`        | 
| Job          | [dbt-cloud job get-artifact](#dbt-cloud-job-get-artifact) | ❌      | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/jobs/{job_id}/artifacts/{remainder}`                                                    | 
| Job          | [dbt-cloud job export](#dbt-cloud-job-export)         | ✅          | Uses a composition of one or more endpoints         | 
| Job          | [dbt-cloud job import](#dbt-cloud-job-import)         | ✅          | Uses a composition of one or more endpoints         | 
| Run          | [dbt-cloud run get](#dbt-cloud-run-get)               | ✅          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/runs/{id}/`         |  
| Run          | [dbt-cloud run list](#dbt-cloud-run-list)             | ✅          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/runs/`              | 
| Run          | [dbt-cloud run cancel](#dbt-cloud-run-cancel)         | ✅          | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/runs/{run_id}/cancel/`                                                    |  
| Run          | [dbt-cloud run cancel-all](#dbt-cloud-run-cancel-all) | ✅          | Uses a composition of one or more endpoints         |  
| Run          | [dbt-cloud run list-artifacts](#dbt-cloud-run-list-artifacts) | ✅          |  GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/runs/{run_id}/artifacts/`                                                | 
| Run          | [dbt-cloud run get-artifact](#dbt-cloud-run-get-artifact) | ✅          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/runs/{run_id}/artifacts/{remainder}`                                                | 
| Run          | [dbt-cloud run get-step](#dbt-cloud-run-get-step)     | ❌          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/steps/{id}/`       | 
| User         | [dbt-cloud user get](#dbt-cloud-user-get)             | ❌          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/users/{id}/`       | 
| User         | [dbt-cloud user list](#dbt-cloud-user-list)           | ❌          | GET `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/users/`            | 
| User         | [dbt-cloud user update](#dbt-cloud-user-update)       | ❌          | POST `https://{dbt_cloud_host}/api/v2/accounts/{account_id}/users/{id}/`      | 
| Metadata     | [dbt-cloud metadata query](#dbt-cloud-metadata-query) | ✅          | POST `https://{dbt_cloud_host}/graphql/`                                      | 



## dbt-cloud account get
This command retrieves dbt Cloud account information.

### Usage
```bash
dbt-cloud account get --account-id 123456
```

[Click to view sample response](tests/data/account_get_response.json)

## dbt-cloud account list
This command retrieves all available dbt Cloud accounts.

### Usage
```bash
dbt-cloud account list
```
[Click to view sample response](tests/data/account_list_response.json)

## dbt-cloud audit-log get

❗ **Available for Enterprise accounts only.**

This command retrieves audit logs for the dbt Cloud account.

### Usage
```bash
dbt-cloud audit-log get --logged-at-start 2022-05-01 --logged-at-end 2022-05-07 --limit 1
```
[Click to view sample response](tests/data/audit_log_get_response.json)

## dbt-cloud project create
This command creates a new dbt Cloud project in a given account.

### Usage
```bash
dbt-cloud project create --name "My project"
```

[Click to view sample response](tests/data/project_create_response.json)

## dbt-cloud project delete
This command deletes a dbt Cloud project in a given account.

### Usage
```bash
dbt-cloud project delete --project-id 273731
```

[Click to view sample response](tests/data/project_delete_response.json)

## dbt-cloud project get
This command retrieves dbt Cloud project information.

### Usage
```bash
dbt-cloud project get --project-id 123457
```

[Click to view sample response](tests/data/project_get_response.json)


## dbt-cloud project list
This command returns a list of projects in the account.

### Usage
```bash
dbt-cloud project list
```

[Click to view sample response](tests/data/project_list_response.json)


## dbt-cloud project update
This command updates a project in a given account.

### Usage
```bash
dbt-cloud project update --project-id 273745 --name "My project renamed"
```

[Click to view sample response](tests/data/project_update_response.json)

## dbt-cloud environment create
This command a new dbt Cloud environment in a given project.

### Usage
```bash
dbt-cloud environment create --account-id 123456 --project-id 123457 --name "My environment" --dbt-version "1.5.0-latest"
```

[Click to view sample response](tests/data/environment_create_response.json)

## dbt-cloud environment delete
This command deletes a dbt Cloud environment in a given project.

### Usage
```bash
dbt-cloud environment delete --account-id 123456 --project-id 123457 --environment-id 40480
```

[Click to view sample response](tests/data/environment_delete_response.json)


## dbt-cloud environment list
This command retrieves environments in a given project.

### Usage
```bash
dbt-cloud environment list --account-id 123456 --project-id 123457 --limit 1
```

[Click to view sample response](tests/data/environment_list_response.json)

## dbt-cloud environment get
This command retrieves information about an environment in a given project.

### Usage
```bash
dbt-cloud environment get --account-id 123456 --project-id 123457 --environment-id 67890
```

[Click to view sample response](tests/data/environment_get_response.json)


## dbt-cloud connection create
This command creates a new database connection in a given project. Supported connection types:

* `snowflake`: Connection to a Snowflake database. Has inout validation for connection parameters.
* `bigquery`: Connection to a Google BigQuery database. No input validation.
* `postgres`: Connection to a PostgreSQL database. No input validation.
* `redshift`: Connection to an Amazon Redshift database. No input validation.
* `adapter`: Connection to a database using a custom dbt Cloud adapter. No input validation.


### Usage
```bash
dbt-cloud connection create --account-id 54321 --project-id 123467 --name Snowflake --type snowflake --account snowflake_account --database analytics --warehouse transforming --role transformer --allow-sso False --client-session-keep-alive False
```

[Click to view sample response](tests/data/connection_create_response.json)


## dbt-cloud connection delete
This command deletes a database connection in a given project.

### Usage
```bash
dbt-cloud connection delete --account-id 54321 --project-id 123467 --connection-id 56901
```

[Click to view sample response](tests/data/connection_delete_response.json)

## dbt-cloud connection list
This command retrievies details of dbt Cloud database connections in a given project.

### Usage
```bash
dbt-cloud connection list --account-id 54321 --project-id 123467 --limit 1
```

[Click to view sample response](tests/data/connection_list_response.json)

## dbt-cloud connection get
This command retrievies the details of a dbt Cloud database connection.

### Usage
```bash
dbt-cloud connection get --account-id 54321 --project-id 123467 --connection-id 56901
```

[Click to view sample response](tests/data/connection_get_response.json)

## dbt-cloud job run
This command triggers a dbt Cloud job run and returns a run status JSON response.

### Usage
```bash
>> dbt-cloud job run --job-id 43167 --cause "My first run!" --steps-override '["dbt seed", "dbt run"]' --wait
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: STARTING ...
Job 43167 run 34929305: RUNNING ...
Job 43167 run 34929305: SUCCESS ...
```

[Click to view sample response](tests/data/job_run_response.json)


## dbt-cloud job get
This command returns the details of a dbt Cloud job.

### Usage
```bash
dbt-cloud job get --job-id 43167
```

[Click to view sample response](tests/data/job_get_response.json)


## dbt-cloud job list
This command returns a list of jobs in the account.

### Usage
```bash
dbt-cloud job list --account-id 123456 --project-id 123457 --limit 2
```

[Click to view sample response](tests/data/job_list_response.json)

## dbt-cloud job create

This command creates a job in a dbt Cloud project.

### Usage
```bash
dbt-cloud job create --project-id 12345 --environment-id 49819 --name "Create job" --execute-steps '["dbt seed", "dbt run"]'
```

[Click to view sample response](tests/data/job_create_response.json)

## dbt-cloud job delete

This command deletes a job in a dbt Cloud project.

### Usage
```bash
dbt-cloud job delete --job-id 48474
```

[Click to view sample response](tests/data/job_delete_response.json)


## dbt-cloud job delete-all

💡 **This is a composition of one or more base commands.**

This command fetches all jobs on the account, deletes them one-by-one after user confirmation via prompt and prints out the job delete responses.

### Usage
```bash
>> dbt-cloud job delete-all --keep-jobs "[43167, 49663]"
Jobs to delete: [54658, 54659]
Delete job 54658? [y/N]: yes
Job 54658 was deleted.
Delete job 54659? [y/N]: yes
Job 54659 was deleted.
```

## dbt-cloud job export

💡 **This is a composition of one or more base commands.**

This command exports a dbt Cloud job as JSON to a file and can be used in conjunction with [dbt-cloud job import](#dbt-cloud-job-import) to copy jobs between dbt Cloud projects.

### Usage
```bash
dbt-cloud job export > job.json
```

## dbt-cloud job import

💡 **This is a composition of one or more base commands.**

This command imports a dbt Cloud job from exported JSON. You can use JSON manipulation tools (e.g., [jq](https://stedolan.github.io/jq/)) to modify the job definition before importing it.

### Usage
```bash
dbt-cloud job export > job.json
cat job.json | jq '.environment_id = 49819 | .name = "Imported job"' | dbt-cloud job import
```

## dbt-cloud run get
This command returns the details of a dbt Cloud run.

### Usage
```bash
dbt-cloud run get --run-id 36053848
```

[Click to view sample response](tests/data/run_get_response.json)

## dbt-cloud run list
This command returns a list of runs in the account.

### Usage
```bash
dbt-cloud run list --limit 2
```

[Click to view sample response](tests/data/run_list_response.json)

## dbt-cloud run cancel
This command cancels a dbt Cloud run. A run can be 'cancelled' irregardless of it's previous status. This means that you can send a request to cancel a previously successful / errored run (and nothing happens practically) and the response status would be similar to cancelling a currently queued or running run.

### Usage
```bash
dbt-cloud run cancel --run-id 36053848
```

[Click to view sample response](tests/data/run_cancel_response.json)

## dbt-cloud run cancel-all

💡 **This is a composition of one or more base commands.**

This command fetches all runs on the account, cancels them one-by-one after user confirmation via prompt and prints out the run cancellation responses. 

You should typically use this with a `--status` arg of either `Running` or `Queued` as cancellations can be requested against all runs. Without this, you will effectively be trying to cancel all runs that had ever been scheduled in the project irregardless of its' current status (which could take a long time if your project has had a lot of previous runs).

### Usage
```bash
>> dbt-cloud run cancel-all --status Running
Runs to cancel: [36053848]
Cancel run 36053848? [y/N]: yes
Run 36053848 has been cancelled.
```

## dbt-cloud run list-artifacts
This command fetches a list of artifact files generated for a completed run.

### Usage
```bash
dbt-cloud run list-artifacts --run-id 36053848
```

[Click to view sample response](tests/data/run_list_artifacts_response.json)

## dbt-cloud run get-artifact
This command fetches an artifact file from a completed run. Once a run has completed, you can use this command to download the manifest.json, run_results.json or catalog.json files from dbt Cloud. These artifacts contain information about the models in your dbt project, timing information around their execution, and a status message indicating the result of the model build.

### Usage
```bash
dbt-cloud run get-artifact --run-id 36053848 --path manifest.json > manifest.json
```

## dbt-cloud metadata query
This command queries the dbt Cloud Metadata API using GraphQL.

### Usage
```bash
dbt-cloud metadata query -f query.graphql
```

[Click to view sample query](tests/data/metadata_query.graphql)


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
