import click
from typing import Optional, Dict
from pydantic import Field
from dbt_cloud.command.command import DbtCloudBaseModel


class Catalog(DbtCloudBaseModel):
    """Represents a dbt catalog.json artifact."""

    metadata: Dict
    nodes: Dict
    nodes: Dict
    errors: Optional[Dict]


@click.group()
def catalog():
    pass


@catalog.command(help="Explores a dbt catalog.json artifact.")
def explore(**kwargs):
    catalog = Catalog.parse_file("catalog.json")
    print(catalog)
