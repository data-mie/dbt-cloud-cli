import click
from typing import Optional, Dict
from pydantic import Field
from dbt_cloud.command.command import DbtCloudBaseModel


class Column(DbtCloudBaseModel):
    """Represents a column in the Catalog."""

    type: str
    index: int
    name: str
    comment: Optional[str]

    def __str__(self):
        return f"{self.name} (type: {self.type}, index: {self.index}, comment: {self.comment})"


class Node(DbtCloudBaseModel):
    """Represents a node in the Catalog."""

    unique_id: str
    metadata: Dict[str, Optional[str]]
    columns: Dict[str, Column]
    stats: Dict[str, Dict]

    @property
    def name(self):
        return self.metadata["name"]

    def __str__(self):
        return f"{self.name} (type: {self.metadata['type']}, schema: {self.metadata['schema']}, database: {self.metadata['database']})"


class Catalog(DbtCloudBaseModel):
    """Represents a dbt catalog.json artifact."""

    metadata: Dict
    nodes: Dict[str, Node]
    sources: Dict
    errors: Optional[Dict]


@click.command(help="An inteactive application for exploring catalog artifacts.")
def data_catalog(**kwargs):
    import inquirer

    catalog = Catalog.parse_file("catalog.json")
    nodes = {node.name: node for node in catalog.nodes.values()}

    while True:
        attribute_options = [
            inquirer.List(
                "attribute",
                message="Select attribute to explore",
                choices=["metadata", "sources", "nodes"],
            )
        ]
        attribute = inquirer.prompt(attribute_options)["attribute"]

        if attribute == "nodes":
            while True:
                node_options = [
                    inquirer.List("node", message="Select node", choices=nodes.values())
                ]
                node_selected = inquirer.prompt(node_options)["node"]
                click.echo(f"{node_selected.name} columns:")
                for column in node_selected.columns.values():
                    click.echo(f"- {column}")
                if not click.confirm("Explore another node?"):
                    break
        else:
            click.echo(getattr(catalog, attribute))
        if not click.confirm("Explore another attribute?"):
            break
