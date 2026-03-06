[![CircleCI](https://circleci.com/gh/data-mie/dbt-cloud-cli/tree/main.svg?style=svg)](https://circleci.com/gh/data-mie/dbt-cloud-cli/tree/main)

> [!NOTE]
> `dbt-cloud-cli` wraps the [dbt Cloud REST API](https://docs.getdbt.com/dbt-cloud/api-v2). It is **not** the same as the [dbt Cloud CLI](https://docs.getdbt.com/docs/cloud/cloud-cli-installation), which runs dbt commands against a Cloud development environment.

# dbt-cloud-cli

A command-line interface and Python library for the [dbt Cloud API](https://docs.getdbt.com/dbt-cloud/api-v2). Use it to trigger jobs, manage resources, and download run artifacts from a terminal, a CI/CD pipeline, or an AI agent.

## Quick start

```bash
pip install dbt-cloud-cli

export DBT_CLOUD_API_TOKEN=<your token>
export DBT_CLOUD_ACCOUNT_ID=<your account id>

# Trigger a job and wait for it to finish
dbt-cloud job run --job-id 43167 --cause "Triggered from CLI" --wait
```

Output (status messages go to stderr, JSON response to stdout):

```
Job 43167 run 34929305: QUEUED ...
Job 43167 run 34929305: RUNNING ...
Job 43167 run 34929305: SUCCESS ...
{"status": {"code": 200, ...}, "data": {"id": 34929305, ...}}
```

## Installation

Requires Python 3.8+.

```bash
pip install dbt-cloud-cli
```

Docker:

```bash
docker run datamie/dbt-cloud-cli:latest
```

## Configuration

Set these environment variables to avoid repeating flags on every command:

| Variable | CLI flag | Description |
|---|---|---|
| `DBT_CLOUD_API_TOKEN` | `--api-token` | dbt Cloud API token |
| `DBT_CLOUD_ACCOUNT_ID` | `--account-id` | Numeric account ID |
| `DBT_CLOUD_HOST` | `--dbt-cloud-host` | API host (default: `cloud.getdbt.com`) |
| `DBT_CLOUD_JOB_ID` | `--job-id` | Numeric job ID |
| `DBT_CLOUD_READONLY` | (none) | Set to `true` to block all write commands (safe for read-only agent contexts) |

## Use cases

- **CI/CD pipelines**: Trigger a job on every PR merge and fail the pipeline if it errors
- **Job management**: Create, copy, and delete jobs across dbt Cloud projects with `job export` / `job import`
- **Artifact downloads**: Pull `manifest.json`, `run_results.json`, or `catalog.json` after a run
- **AI agents**: Use the Python library interface to give an LLM agent access to dbt Cloud operations

---

## Using as a Python library (for AI agents)

`dbt-cloud-cli` ships pre-built tool definitions for [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling) and [Anthropic tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use), generated directly from the same Pydantic models that power the CLI.

```python
from dbt_cloud.tools import get_openai_tools, get_anthropic_tools, execute_tool_call
import os

os.environ["DBT_CLOUD_API_TOKEN"] = "<your token>"
os.environ["DBT_CLOUD_ACCOUNT_ID"] = "123456"  # or set per call
```

### OpenAI

```python
import openai
from dbt_cloud.tools import get_openai_tools, execute_tool_call

client = openai.OpenAI()
tools = get_openai_tools()  # or get_openai_tools(include=["job_run", "run_get"])

messages = [{"role": "user", "content": "Run job 43167 and tell me if it succeeded."}]
response = client.chat.completions.create(model="gpt-4o", tools=tools, messages=messages)

for tool_call in response.choices[0].message.tool_calls or []:
    result = execute_tool_call(tool_call.function.name, json.loads(tool_call.function.arguments))
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
```

### Anthropic

```python
import anthropic
from dbt_cloud.tools import get_anthropic_tools, execute_tool_call

client = anthropic.Anthropic()
tools = get_anthropic_tools()  # or get_anthropic_tools(include=["job_run", "run_get"])

response = client.messages.create(
    model="claude-opus-4-6",
    tools=tools,
    messages=[{"role": "user", "content": "Run job 43167 and tell me if it succeeded."}],
)

for block in response.content:
    if block.type == "tool_use":
        result = execute_tool_call(block.name, block.input)
        # append tool_result to messages and continue the loop
```

### Direct execution (no LLM)

```python
from dbt_cloud.tools import execute_tool_call

result = execute_tool_call("job_run", {"account_id": 123456, "job_id": 43167, "cause": "nightly"})
print(result["data"]["id"])  # run ID
```

### Available tools

All 27 tools are available. Use `include` to expose only what the agent needs:

```python
# Read-only agent — can inspect but not mutate
tools = get_anthropic_tools(include=[
    "job_get", "job_list",
    "run_get", "run_list", "run_list_artifacts", "run_get_artifact",
    "project_get", "project_list",
    "environment_get", "environment_list",
])
```

For headless/production deployments, set `DBT_CLOUD_READONLY=true` to enforce this at the environment level.

---

## Commands

For full argument reference, run `dbt-cloud <command> --help`.

| Group | Command | API |
|---|---|---|
| Account | [account get](#dbt-cloud-account-get) | GET `/api/v2/accounts/{id}/` |
| Account | [account list](#dbt-cloud-account-list) | GET `/api/v3/accounts/` |
| Audit log | [audit-log get](#dbt-cloud-audit-log-get) | GET `/api/v3/audit-logs/` |
| Project | [project create](#dbt-cloud-project-create) | POST `/api/v3/accounts/{id}/projects/` |
| Project | [project delete](#dbt-cloud-project-delete) | DELETE `/api/v3/accounts/{id}/projects/{id}/` |
| Project | [project get](#dbt-cloud-project-get) | GET `/api/v3/accounts/{id}/projects/{id}/` |
| Project | [project list](#dbt-cloud-project-list) | GET `/api/v3/accounts/{id}/projects/` |
| Project | [project update](#dbt-cloud-project-update) | POST `/api/v3/accounts/{id}/projects/{id}/` |
| Environment | [environment create](#dbt-cloud-environment-create) | POST `/api/v3/accounts/{id}/environments/` |
| Environment | [environment delete](#dbt-cloud-environment-delete) | DELETE `/api/v3/accounts/{id}/environments/{id}/` |
| Environment | [environment get](#dbt-cloud-environment-get) | GET `/api/v3/accounts/{id}/environments/{id}/` |
| Environment | [environment list](#dbt-cloud-environment-list) | GET `/api/v3/accounts/{id}/environments/` |
| Connection | [connection create](#dbt-cloud-connection-create) | POST `/api/v3/accounts/{id}/projects/{id}/connections/` |
| Connection | [connection delete](#dbt-cloud-connection-delete) | DELETE `/api/v3/accounts/{id}/projects/{id}/connections/{id}/` |
| Connection | [connection get](#dbt-cloud-connection-get) | GET `/api/v3/accounts/{id}/projects/{id}/connections/{id}/` |
| Connection | [connection list](#dbt-cloud-connection-list) | GET `/api/v3/accounts/{id}/projects/{id}/connections/` |
| Job | [job create](#dbt-cloud-job-create) | POST `/api/v2/accounts/{id}/jobs/` |
| Job | [job delete](#dbt-cloud-job-delete) | DELETE `/api/v2/accounts/{id}/jobs/{id}/` |
| Job | [job delete-all](#dbt-cloud-job-delete-all) | (composite) |
| Job | [job export](#dbt-cloud-job-export) | (composite) |
| Job | [job get](#dbt-cloud-job-get) | GET `/api/v2/accounts/{id}/jobs/{id}/` |
| Job | [job import](#dbt-cloud-job-import) | (composite) |
| Job | [job list](#dbt-cloud-job-list) | GET `/api/v2/accounts/{id}/jobs/` |
| Job | [job run](#dbt-cloud-job-run) | POST `/api/v2/accounts/{id}/jobs/{id}/run/` |
| Run | [run cancel](#dbt-cloud-run-cancel) | POST `/api/v2/accounts/{id}/runs/{id}/cancel/` |
| Run | [run cancel-all](#dbt-cloud-run-cancel-all) | (composite) |
| Run | [run get](#dbt-cloud-run-get) | GET `/api/v2/accounts/{id}/runs/{id}/` |
| Run | [run get-artifact](#dbt-cloud-run-get-artifact) | GET `/api/v2/accounts/{id}/runs/{id}/artifacts/{path}` |
| Run | [run list](#dbt-cloud-run-list) | GET `/api/v2/accounts/{id}/runs/` |
| Run | [run list-artifacts](#dbt-cloud-run-list-artifacts) | GET `/api/v2/accounts/{id}/runs/{id}/artifacts/` |
| Metadata | [metadata query](#dbt-cloud-metadata-query) | POST `/graphql/` |

---

## Command reference

### dbt-cloud account get

Retrieves dbt Cloud account information.

```bash
dbt-cloud account get --account-id 123456
```

[Sample response](tests/data/account_get_response.json)

---

### dbt-cloud account list

Lists all dbt Cloud accounts accessible with the current API token.

```bash
dbt-cloud account list
```

[Sample response](tests/data/account_list_response.json)

---

### dbt-cloud audit-log get

> Enterprise accounts only.

Retrieves audit logs for a dbt Cloud account.

```bash
dbt-cloud audit-log get --logged-at-start 2022-05-01 --logged-at-end 2022-05-07 --limit 1
```

[Sample response](tests/data/audit_log_get_response.json)

---

### dbt-cloud project create

Creates a new dbt Cloud project.

```bash
dbt-cloud project create --name "My project" --type 0
```

[Sample response](tests/data/project_create_response.json)

---

### dbt-cloud project delete

Deletes a dbt Cloud project.

```bash
dbt-cloud project delete --project-id 273731
```

[Sample response](tests/data/project_delete_response.json)

---

### dbt-cloud project get

Retrieves dbt Cloud project details.

```bash
dbt-cloud project get --project-id 123457
```

[Sample response](tests/data/project_get_response.json)

---

### dbt-cloud project list

Lists all projects in an account.

```bash
dbt-cloud project list
```

[Sample response](tests/data/project_list_response.json)

---

### dbt-cloud project update

Updates a project.

```bash
dbt-cloud project update --project-id 273745 --name "My project renamed"
```

[Sample response](tests/data/project_update_response.json)

---

### dbt-cloud environment create

Creates a new environment in a dbt Cloud project.

```bash
dbt-cloud environment create --project-id 123457 --name "Production" --type deployment --dbt-version "1.8.0-latest"
```

[Sample response](tests/data/environment_create_response.json)

---

### dbt-cloud environment delete

Deletes an environment.

```bash
dbt-cloud environment delete --project-id 123457 --environment-id 40480
```

[Sample response](tests/data/environment_delete_response.json)

---

### dbt-cloud environment get

Retrieves details of an environment.

```bash
dbt-cloud environment get --project-id 123457 --environment-id 67890
```

[Sample response](tests/data/environment_get_response.json)

---

### dbt-cloud environment list

Lists environments in a project.

```bash
dbt-cloud environment list --project-id 123457
```

[Sample response](tests/data/environment_list_response.json)

---

### dbt-cloud connection create

Creates a database connection in a project. Supported types: `snowflake`, `bigquery`, `postgres`, `redshift`, `adapter`.

```bash
dbt-cloud connection create \
  --project-id 123467 \
  --name Snowflake \
  --type snowflake \
  --account snowflake_account \
  --database analytics \
  --warehouse transforming \
  --role transformer \
  --allow-sso False \
  --client-session-keep-alive False
```

[Sample response](tests/data/connection_create_response.json)

---

### dbt-cloud connection delete

Deletes a database connection.

```bash
dbt-cloud connection delete --project-id 123467 --connection-id 56901
```

[Sample response](tests/data/connection_delete_response.json)

---

### dbt-cloud connection get

Retrieves details of a database connection.

```bash
dbt-cloud connection get --project-id 123467 --connection-id 56901
```

[Sample response](tests/data/connection_get_response.json)

---

### dbt-cloud connection list

Lists database connections in a project.

```bash
dbt-cloud connection list --project-id 123467
```

[Sample response](tests/data/connection_list_response.json)

---

### dbt-cloud job run

Triggers a dbt Cloud job run. Use `--wait` to poll until completion.

```bash
dbt-cloud job run --job-id 43167 --cause "My first run!" --wait
```

```bash
# Override steps for this run only
dbt-cloud job run --job-id 43167 --steps-override '["dbt seed", "dbt run"]' --wait
```

[Sample response](tests/data/job_run_response.json)

---

### dbt-cloud job get

Returns details of a dbt Cloud job.

```bash
dbt-cloud job get --job-id 43167
```

[Sample response](tests/data/job_get_response.json)

---

### dbt-cloud job list

Lists jobs in an account.

```bash
dbt-cloud job list --project-id 123457 --limit 20
```

[Sample response](tests/data/job_list_response.json)

---

### dbt-cloud job create

Creates a job in a dbt Cloud project.

```bash
dbt-cloud job create \
  --project-id 12345 \
  --environment-id 49819 \
  --name "Nightly run" \
  --execute-steps '["dbt seed", "dbt run", "dbt test"]' \
  --job-type scheduled
```

[Sample response](tests/data/job_create_response.json)

---

### dbt-cloud job delete

Deletes a job.

```bash
dbt-cloud job delete --job-id 48474
```

[Sample response](tests/data/job_delete_response.json)

---

### dbt-cloud job delete-all

> Composite command.

Lists all jobs in the account and deletes them one-by-one with confirmation prompts. Use `--keep-jobs` to exclude specific job IDs, and `--yes` to skip prompts.

```bash
dbt-cloud job delete-all --keep-jobs "[43167, 49663]"
```

```
Jobs to delete: [54658, 54659]
Delete job 54658? [y/N]: yes
Job 54658 was deleted.
Delete job 54659? [y/N]: yes
Job 54659 was deleted.
```

---

### dbt-cloud job export

> Composite command.

Exports a job definition as JSON. Use with [job import](#dbt-cloud-job-import) to copy jobs between projects.

```bash
dbt-cloud job export --job-id 43167 > job.json
```

---

### dbt-cloud job import

> Composite command.

Imports a job from exported JSON. Pipe through `jq` to modify fields before importing.

```bash
dbt-cloud job export --job-id 43167 \
  | jq '.environment_id = 49819 | .name = "Imported job"' \
  | dbt-cloud job import
```

---

### dbt-cloud run get

Returns details of a run.

```bash
dbt-cloud run get --run-id 36053848
```

[Sample response](tests/data/run_get_response.json)

---

### dbt-cloud run list

Lists runs in an account.

```bash
dbt-cloud run list --limit 20
```

[Sample response](tests/data/run_list_response.json)

---

### dbt-cloud run cancel

Cancels a run. Can be sent against a run in any state (has no effect if the run has already completed).

```bash
dbt-cloud run cancel --run-id 36053848
```

[Sample response](tests/data/run_cancel_response.json)

---

### dbt-cloud run cancel-all

> Composite command.

Cancels runs with confirmation prompts. Use `--status` to filter by run state (typically `Running` or `Queued`).

```bash
dbt-cloud run cancel-all --status Running
```

```
Runs to cancel: [36053848]
Cancel run 36053848? [y/N]: yes
Run 36053848 has been cancelled.
```

---

### dbt-cloud run list-artifacts

Lists artifact files generated for a completed run.

```bash
dbt-cloud run list-artifacts --run-id 36053848
```

[Sample response](tests/data/run_list_artifacts_response.json)

---

### dbt-cloud run get-artifact

Downloads an artifact file from a completed run. Supports `manifest.json`, `run_results.json`, `catalog.json`, and others.

```bash
dbt-cloud run get-artifact --run-id 36053848 --path manifest.json > manifest.json
```

---

### dbt-cloud metadata query

Queries the dbt Cloud Metadata API using GraphQL.

```bash
dbt-cloud metadata query -f query.graphql
```

Or pipe a query directly:

```bash
echo '{
  model(jobId: 49663, uniqueId: "model.jaffle_shop.customers") {
    parentsModels { runId uniqueId executionTime }
    parentsSources { runId uniqueId state }
  }
}' | dbt-cloud metadata query
```

[Sample query](tests/data/metadata_query.graphql)

---

## Demo utilities

Install with the `demo` extra:

```bash
pip install dbt-cloud-cli[demo]
```

### dbt-cloud demo data-catalog

An interactive CLI for exploring `catalog.json` artifacts.

```bash
latest_run_id=$(dbt-cloud run list --job-id $DBT_CLOUD_JOB_ID --limit 1 | jq .data[0].id -r)
dbt-cloud run get-artifact --run-id $latest_run_id --path catalog.json > catalog.json
dbt-cloud demo data-catalog -f catalog.json
```

---

## Acknowledgements

Thanks to [Sean McIntyre](https://github.com/boxysean) for his initial work on triggering a dbt Cloud job using Python as proposed in [this post on dbt Discourse](https://discourse.getdbt.com/t/triggering-a-dbt-cloud-job-in-your-automated-workflow-with-python/2573).
