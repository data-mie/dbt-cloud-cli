FROM python:3.9-alpine

ENV APP_HOME=/dbt-cloud-cli
WORKDIR $APP_HOME

COPY setup.py README.md ./
COPY dbt_cloud ./dbt_cloud/

RUN pip install --no-cache-dir .

ENTRYPOINT ["dbt-cloud"]