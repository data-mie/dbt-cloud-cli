from dbt_cloud.job import DbtCloudJob, DbtCloudJobCreateArgs


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
