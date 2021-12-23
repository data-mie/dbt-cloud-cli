from dbt_cloud.job import DbtCloudJob, DbtCloudJobCreateArgs, DbtCloudJobRunArgs


def test_mock_job_get(requests_mock, job, job_get_response):
    url = job.get_api_url() + "/"
    requests_mock.get(url, json=job_get_response, status_code=200)
    response = job.get()
    assert response.json() == job_get_response


def test_mock_job_create(
    requests_mock, job, job_create_response, project_id, environment_id
):
    url = job.get_api_url() + "/"
    requests_mock.post(url, json=job_create_response, status_code=201)
    args = DbtCloudJobCreateArgs(
        project_id=project_id,
        environment_id=environment_id,
        name="Dummy job",
        execute_steps=["dbt seed", "dbt run"],
    )
    response = job.create(args)
    assert response.json() == job_create_response


def test_mock_job_run(requests_mock, job, job_run_response):
    url = job.get_api_url() + "/run/"
    requests_mock.post(url, json=job_run_response, status_code=200)
    args = DbtCloudJobRunArgs()
    response, job_run = job.run(args)
    assert response.json() == job_run_response
    assert job_run.run_id == job_run_response["data"]["id"]
