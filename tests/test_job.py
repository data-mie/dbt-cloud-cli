from dbt_cloud.job import DbtCloudJob, DbtCloudJobCreateArgs, DbtCloudJobRunArgs


def test_mock_job_get(mock_job_api, job, job_get_response):
    response = job.get()
    assert response.json() == job_get_response


def test_mock_job_create(
    mock_job_api, job, job_create_response, project_id, environment_id
):
    args = DbtCloudJobCreateArgs(
        project_id=project_id,
        environment_id=environment_id,
        name="Dummy job",
        execute_steps=["dbt seed", "dbt run"],
    )
    response = job.create(args)
    assert response.json() == job_create_response


def test_mock_job_run(mock_job_api, job, job_run_response):
    args = DbtCloudJobRunArgs()
    response, job_run = job.run(args)
    assert response.json() == job_run_response
    assert job_run.run_id == job_run_response["data"]["id"]
