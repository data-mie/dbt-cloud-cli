from dbt_cloud.run import DbtCloudRun, DbtCloudRunStatus


def test_mock_run_get_status(requests_mock, run, run_get_response):
    url = run.get_api_url() + "/"
    requests_mock.get(url, json=run_get_response, status_code=200)
    response, run_status = run.get_status()
    assert response.json() == run_get_response
    assert run_status == DbtCloudRunStatus.SUCCESS


def test_mock_run_list_artifacts(requests_mock, run, run_list_artifacts_response):
    url = run.get_api_url() + "/artifacts/"
    requests_mock.get(url, json=run_list_artifacts_response, status_code=200)
    response = run.list_artifacts()
    assert response.json() == run_list_artifacts_response
