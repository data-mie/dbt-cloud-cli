import os
import sys
import logging
import time
import click
import requests
from dbt_cloud.command import (
    DbtCloudRunStatus,
    DbtCloudJobGetCommand,
    DbtCloudJobCreateCommand,
    DbtCloudJobDeleteCommand,
    DbtCloudJobRunCommand,
    DbtCloudAccountCommand,
    DbtCloudRunGetCommand,
    DbtCloudRunListArtifactsCommand,
    DbtCloudRunGetArtifactCommand,
    DbtCloudMetadataQueryCommand,
    DbtCloudRunListCommand,
    DbtCloudRunCancelCommand,
    DbtCloudJobListCommand,
    DbtCloudProjectGetCommand,
    DbtCloudProjectListCommand,
    DbtCloudProjectCreateCommand,
    DbtCloudProjectDeleteCommand,
    DbtCloudProjectUpdateCommand,
    DbtCloudEnvironmentListCommand,
    DbtCloudEnvironmentGetCommand,
    DbtCloudEnvironmentCreateCommand,
    DbtCloudEnvironmentDeleteCommand,
    DbtCloudAccountListCommand,
    DbtCloudAccountGetCommand,
    DbtCloudAuditLogGetCommand,
    DbtCloudConnectionCreateCommand,
    DbtCloudConnectionDeleteCommand,
    DbtCloudConnectionGetCommand,
    DbtCloudConnectionListCommand,
)
from dbt_cloud.demo import data_catalog
from dbt_cloud.serde import json_to_dict, dict_to_json
from dbt_cloud.field import PythonLiteralOption


def _assert_write_access():
    """Exit with a clear error if DBT_CLOUD_READONLY is set to a truthy value."""
    if os.environ.get("DBT_CLOUD_READONLY", "").lower() in ("1", "true", "yes"):
        click.echo(
            "Error: readonly mode is enabled (DBT_CLOUD_READONLY=true). "
            "Unset DBT_CLOUD_READONLY to allow mutating commands.",
            err=True,
        )
        sys.exit(1)


def _format_job(data):
    steps = ", ".join(data.get("execute_steps") or [])
    schedule = data.get("cron_humanized") or "N/A"
    return (
        f"Job {data['id']}: {data['name']}\n"
        f"  Steps:    {steps}\n"
        f"  Schedule: {schedule}"
    )


def _format_job_list(items):
    if not items:
        return "No jobs found."
    lines = [f"{'ID':<10} {'NAME':<35} STEPS"]
    lines.append("-" * 70)
    for job in items:
        steps = ", ".join(job.get("execute_steps") or [])
        lines.append(f"{job['id']:<10} {job['name']:<35} {steps}")
    return "\n".join(lines)


def _format_run(data):
    status = data.get("status_humanized") or str(data.get("status", "N/A"))
    duration = data.get("duration_humanized") or data.get("duration") or "N/A"
    job_id = data.get("job_definition_id") or data.get("job_id", "N/A")
    branch = data.get("git_branch") or "N/A"
    url = data.get("href") or "N/A"
    return (
        f"Run {data['id']}: {status} ({duration})\n"
        f"  Job:    {job_id}\n"
        f"  Branch: {branch}\n"
        f"  URL:    {url}"
    )


def _format_run_list(items):
    if not items:
        return "No runs found."
    lines = [f"{'ID':<12} {'STATUS':<14} {'JOB':<10} DURATION"]
    lines.append("-" * 55)
    for run in items:
        status = run.get("status_humanized") or str(run.get("status", "N/A"))
        job_id = str(run.get("job_definition_id") or run.get("job_id", "N/A"))
        duration = run.get("duration_humanized") or run.get("duration") or "N/A"
        lines.append(f"{str(run['id']):<12} {status:<14} {job_id:<10} {duration}")
    return "\n".join(lines)


_TEXT_FORMATTERS = {
    DbtCloudJobGetCommand: lambda d: _format_job(d.get("data", d)),
    DbtCloudJobListCommand: lambda d: _format_job_list(d.get("data", [])),
    DbtCloudRunGetCommand: lambda d: _format_run(d.get("data", d)),
    DbtCloudRunListCommand: lambda d: _format_run_list(d.get("data", [])),
}


def _output_format():
    ctx = click.get_current_context(silent=True)
    if ctx and ctx.obj:
        return ctx.obj.get("output", "json")
    return "json"


def execute_and_print(command, **kwargs):
    response = command.execute(**kwargs)
    data = response.json()
    fmt = _output_format()
    if fmt == "text":
        formatter = _TEXT_FORMATTERS.get(type(command))
        click.echo(formatter(data) if formatter else dict_to_json(data))
    else:
        click.echo(dict_to_json(data))
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    return response


@click.group(help="The dbt Cloud command line interface.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "text"]),
    default=None,
    envvar="DBT_CLOUD_OUTPUT",
    help="Output format: json (default) or text for human-readable summaries.",
    is_eager=True,
)
@click.pass_context
def dbt_cloud(ctx, output):
    ctx.ensure_object(dict)
    ctx.obj["output"] = output or "json"

    import http.client as http_client

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level)
    requests_logger = logging.getLogger("requests.packages.urllib3")
    requests_logger.setLevel(level)
    requests_logger.propagate = True
    if level == "DEBUG":
        http_client.HTTPConnection.debuglevel = 1


@dbt_cloud.group(help="Interact with dbt Cloud jobs.")
def job():
    pass


@dbt_cloud.group(name="run", help="Interact with dbt Cloud job runs.")
def job_run():
    pass


@dbt_cloud.group(help="Interact with dbt Cloud projects.")
def project():
    pass


@dbt_cloud.group(help="Interact with dbt Cloud environments.")
def environment():
    pass


@dbt_cloud.group(help="Interact with dbt Cloud database connections.")
def connection():
    pass


@dbt_cloud.group(help="Interact with dbt Cloud accounts.")
def account():
    pass


@dbt_cloud.group(help="Interact with dbt Cloud audit logs (Enterprise only).")
def audit_log():
    pass


@dbt_cloud.group(help="Interact with the dbt Cloud Metadata API.")
def metadata():
    pass


@job.command(help=DbtCloudJobRunCommand.get_description())
@DbtCloudJobRunCommand.click_options
@click.option(
    f"--wait/--no-wait",
    default=False,
    help="Wait for the process to finish before returning from the API call.",
)
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Response export file path.",
)
def run(wait, file, **kwargs):
    _assert_write_access()
    command = DbtCloudJobRunCommand.from_click_options(**kwargs)
    response = command.execute()
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        file.write(dict_to_json(response.json()))
        click.echo(str(e), err=True)
        sys.exit(1)

    if wait:
        run_id = response.json()["data"]["id"]
        while True:
            run_get_command = DbtCloudRunGetCommand(
                api_token=command.api_token,
                account_id=command.account_id,
                dbt_cloud_host=command.dbt_cloud_host,
                run_id=run_id,
            )
            response = run_get_command.execute()
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                file.write(dict_to_json(response.json()))
                click.echo(str(e), err=True)
                sys.exit(1)
            status = DbtCloudRunStatus(response.json()["data"]["status"])
            click.echo(
                f"Job {command.job_id} run {run_id}: {status.name} ...", err=True
            )
            if status == DbtCloudRunStatus.SUCCESS:
                break
            elif status in (DbtCloudRunStatus.ERROR, DbtCloudRunStatus.CANCELLED):
                href = response.json()["data"]["href"]
                click.echo(
                    f"Job run failed with {status.name} status. For more information, see {href}.",
                    err=True,
                )
                file.write(dict_to_json(response.json()))
                sys.exit(1)
            time.sleep(5)

    file.write(dict_to_json(response.json()))


@job.command(help=DbtCloudJobListCommand.get_description())
@DbtCloudJobListCommand.click_options
def list(**kwargs):
    command = DbtCloudJobListCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help=DbtCloudJobGetCommand.get_description())
@DbtCloudJobGetCommand.click_options
def get(**kwargs):
    command = DbtCloudJobGetCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help=DbtCloudJobCreateCommand.get_description())
@DbtCloudJobCreateCommand.click_options
def create(**kwargs):
    _assert_write_access()
    command = DbtCloudJobCreateCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help=DbtCloudJobDeleteCommand.get_description())
@DbtCloudJobDeleteCommand.click_options
def delete(**kwargs):
    _assert_write_access()
    command = DbtCloudJobDeleteCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job.command(help="Delete all jobs on the account.")
@DbtCloudJobListCommand.click_options
@click.option(
    "--keep-jobs",
    cls=PythonLiteralOption,
    default=[],
    help="List of job IDs to exclude from deletion.",
)
@click.option("--dry-run", is_flag=True, help="Execute as a dry run.")
@click.option(
    "-y", "--yes", "assume_yes", is_flag=True, help="Automatic yes to prompts."
)
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Response export file path.",
)
def delete_all(keep_jobs, dry_run, file, assume_yes, **kwargs):
    _assert_write_access()
    list_command = DbtCloudJobListCommand.from_click_options(**kwargs)
    response = list_command.execute()
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    job_ids_to_delete = [
        job_dict["id"]
        for job_dict in response.json()["data"]
        if job_dict["id"] not in keep_jobs
    ]
    click.echo(f"Jobs to delete: {job_ids_to_delete}", err=True)
    deleted_job_responses = []
    if not dry_run:
        for job_id in job_ids_to_delete:
            delete_command = DbtCloudJobDeleteCommand(**kwargs, job_id=job_id)
            if assume_yes:
                is_confirmed = True
            else:
                is_confirmed = click.confirm(f"Delete job {job_id}?")
            if is_confirmed:
                response = delete_command.execute()
                try:
                    response.raise_for_status()
                except requests.HTTPError as e:
                    click.echo(str(e), err=True)
                    sys.exit(1)
                deleted_job_responses.append(response.json())
                click.echo(f"Job {job_id} was deleted.", err=True)
    file.write(dict_to_json(deleted_job_responses))


@job.command(help="Exports a dbt Cloud job as JSON to a file.")
@DbtCloudJobGetCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Export file path.",
)
def export(file, **kwargs):
    command = DbtCloudJobGetCommand.from_click_options(**kwargs)
    response = command.execute()
    response.raise_for_status()
    job_dict = response.json()["data"]
    job_dict.pop("id")
    file.write(dict_to_json(job_dict))


@job.command(help="Imports a dbt Cloud job from exported JSON.", name="import")
@DbtCloudAccountCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("r"),
    help="Import file path.",
)
def import_job(file, **kwargs):
    _assert_write_access()
    base_command = DbtCloudAccountCommand.from_click_options(**kwargs)
    job_create_kwargs = {**json_to_dict(file.read()), **base_command.model_dump()}
    command = DbtCloudJobCreateCommand(**job_create_kwargs)
    execute_and_print(command)


@job_run.command(help=DbtCloudRunCancelCommand.get_description())
@DbtCloudRunCancelCommand.click_options
def cancel(**kwargs):
    _assert_write_access()
    command = DbtCloudRunCancelCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job_run.command(help="Cancel all running jobs by status.")
@DbtCloudRunListCommand.click_options
@click.option("--dry-run", is_flag=True, help="Execute as a dry run.")
@click.option(
    "-y", "--yes", "assume_yes", is_flag=True, help="Automatic yes to prompts."
)
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("w"),
    help="Response export file path.",
)
def cancel_all(dry_run, file, assume_yes, **kwargs):
    _assert_write_access()
    list_command = DbtCloudRunListCommand.from_click_options(**kwargs)
    response = list_command.execute()
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    run_ids_to_cancel = [run_dict["id"] for run_dict in response.json()["data"]]
    click.echo(f"Runs to cancel: {run_ids_to_cancel}", err=True)
    cancelled_job_responses = []
    if not dry_run:
        for run_id in run_ids_to_cancel:
            cancel_command = DbtCloudRunCancelCommand(**kwargs, run_id=run_id)
            if assume_yes:
                is_confirmed = True
            else:
                is_confirmed = click.confirm(f"Cancel run {run_id}?")
            if is_confirmed:
                response = cancel_command.execute()
                try:
                    response.raise_for_status()
                except requests.HTTPError as e:
                    click.echo(str(e), err=True)
                    sys.exit(1)
                cancelled_job_responses.append(response.json())
                click.echo(f"Run {run_id} has been cancelled.", err=True)
    file.write(dict_to_json(cancelled_job_responses))


@job_run.command(help=DbtCloudRunGetCommand.get_description())
@DbtCloudRunGetCommand.click_options
def get(**kwargs):
    command = DbtCloudRunGetCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job_run.command(help=DbtCloudRunListArtifactsCommand.get_description())
@DbtCloudRunListArtifactsCommand.click_options
def list_artifacts(**kwargs):
    command = DbtCloudRunListArtifactsCommand.from_click_options(**kwargs)
    execute_and_print(command)


@job_run.command(help=DbtCloudRunListCommand.get_description())
@DbtCloudRunListCommand.click_options
@click.option(
    "--paginate",
    default=False,
    is_flag=True,
    help="Return all runs using pagination (ignores limit and offset).",
)
def list(**kwargs):
    paginate = kwargs.pop("paginate")
    command = DbtCloudRunListCommand.from_click_options(**kwargs)
    if not paginate:
        execute_and_print(command)
    else:
        command.offset = 0
        command.limit = 100
        responses = []
        while True:
            response = command.execute()
            response.raise_for_status()
            responses.append(response)
            command.offset += response.json()["extra"]["pagination"]["count"]
            if command.offset >= response.json()["extra"]["pagination"]["total_count"]:
                break

        # Use last response and append all data to it
        last_response_dict = responses[-1].json()
        last_response_dict["data"] = []
        for response in responses:
            last_response_dict["data"].extend(response.json()["data"])
        last_response_dict["extra"]["pagination"]["count"] = len(
            last_response_dict["data"]
        )
        click.echo(dict_to_json(last_response_dict))


@job_run.command(help=DbtCloudRunGetArtifactCommand.get_description())
@DbtCloudRunGetArtifactCommand.click_options
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("wb"),
    help="Export file path.",
)
def get_artifact(file, **kwargs):
    command = DbtCloudRunGetArtifactCommand.from_click_options(**kwargs)
    response = command.execute()
    file.write(response.content)
    response.raise_for_status()


@project.command(help=DbtCloudProjectGetCommand.get_description())
@DbtCloudProjectGetCommand.click_options
def get(**kwargs):
    command = DbtCloudProjectGetCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@project.command(help=DbtCloudProjectListCommand.get_description())
@DbtCloudProjectListCommand.click_options
def list(**kwargs):
    command = DbtCloudProjectListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@project.command(help=DbtCloudProjectCreateCommand.get_description())
@DbtCloudProjectCreateCommand.click_options
def create(**kwargs):
    _assert_write_access()
    command = DbtCloudProjectCreateCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@project.command(help=DbtCloudProjectDeleteCommand.get_description())
@DbtCloudProjectDeleteCommand.click_options
def delete(**kwargs):
    _assert_write_access()
    command = DbtCloudProjectDeleteCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@project.command(help=DbtCloudProjectUpdateCommand.get_description())
@DbtCloudProjectUpdateCommand.click_options
def update(**kwargs):
    _assert_write_access()
    command = DbtCloudProjectUpdateCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@environment.command(help=DbtCloudEnvironmentListCommand.get_description())
@DbtCloudEnvironmentListCommand.click_options
def list(**kwargs):
    command = DbtCloudEnvironmentListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@environment.command(help=DbtCloudEnvironmentGetCommand.get_description())
@DbtCloudEnvironmentGetCommand.click_options
def get(**kwargs):
    command = DbtCloudEnvironmentGetCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@environment.command(help=DbtCloudEnvironmentCreateCommand.get_description())
@DbtCloudEnvironmentCreateCommand.click_options
def create(**kwargs):
    _assert_write_access()
    command = DbtCloudEnvironmentCreateCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@environment.command(help=DbtCloudEnvironmentDeleteCommand.get_description())
@DbtCloudEnvironmentDeleteCommand.click_options
def delete(**kwargs):
    _assert_write_access()
    command = DbtCloudEnvironmentDeleteCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@connection.command(
    help=DbtCloudConnectionCreateCommand.get_description(),
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
@DbtCloudConnectionCreateCommand.click_options
def create(ctx, **kwargs):
    _assert_write_access()
    keys = ctx.args[::2]  # Every even element is a key
    values = ctx.args[1::2]  # Every odd element is a value

    def _coerce(v):
        if v.lower() == "true":
            return True
        if v.lower() == "false":
            return False
        try:
            return int(v)
        except ValueError:
            pass
        try:
            return float(v)
        except ValueError:
            pass
        return v

    kwargs["details"] = {
        key.lstrip("-").replace("-", "_"): _coerce(value)
        for key, value in zip(keys, values)
    }
    command = DbtCloudConnectionCreateCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@connection.command(help=DbtCloudConnectionDeleteCommand.get_description())
@DbtCloudConnectionDeleteCommand.click_options
def delete(**kwargs):
    _assert_write_access()
    command = DbtCloudConnectionDeleteCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@connection.command(help=DbtCloudConnectionGetCommand.get_description())
@DbtCloudConnectionGetCommand.click_options
def get(**kwargs):
    command = DbtCloudConnectionGetCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@connection.command(help=DbtCloudConnectionListCommand.get_description())
@DbtCloudConnectionListCommand.click_options
def list(**kwargs):
    command = DbtCloudConnectionListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@account.command(help=DbtCloudAccountListCommand.get_description())
@DbtCloudAccountListCommand.click_options
def list(**kwargs):
    command = DbtCloudAccountListCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@account.command(help=DbtCloudAccountGetCommand.get_description())
@DbtCloudAccountGetCommand.click_options
def get(**kwargs):
    command = DbtCloudAccountGetCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@audit_log.command(help=DbtCloudAuditLogGetCommand.get_description())
@DbtCloudAuditLogGetCommand.click_options
def get(**kwargs):
    command = DbtCloudAuditLogGetCommand.from_click_options(**kwargs)
    response = execute_and_print(command)


@metadata.command(help=DbtCloudMetadataQueryCommand.get_description())
@click.option(
    "-f",
    "--file",
    default="-",
    type=click.File("r"),
    help="Read query from file.",
)
@DbtCloudMetadataQueryCommand.click_options
def query(file, **kwargs):
    command = DbtCloudMetadataQueryCommand.from_click_options(
        query=file.read(), **kwargs
    )
    execute_and_print(command)


@dbt_cloud.group(help="Demo applications")
def demo():
    pass


demo.add_command(data_catalog)
