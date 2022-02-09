import click
from typing import Optional, Dict, Any
from pydantic import Field, BaseModel
from dbt_cloud.command.command import DbtCloudBaseModel


class Stats(DbtCloudBaseModel):
    """Represent node stats in the Catalog."""

    id: str
    label: str
    value: Any
    include: bool
    description: str

    def __str__(self):
        return f"{self.label}: {self.value}"


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
    stats: Dict[str, Stats]

    @property
    def name(self):
        return self.metadata["name"]

    @property
    def database(self):
        return self.metadata["database"]

    @property
    def schema(self):
        return self.metadata["schema"]

    @property
    def type(self):
        return self.metadata["type"]

    @property
    def owner(self):
        return self.metadata.get("owner")

    def __str__(self):
        return f"{self.name} (type: {self.type}, schema: {self.schema}, database: {self.database})"

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name


class Catalog(DbtCloudBaseModel):
    """Represents a dbt catalog.json artifact."""

    metadata: Dict
    nodes: Dict[str, Node]
    sources: Dict[str, Node]
    errors: Optional[Dict]


def explore_nodes(nodes: Dict[str, Node], node_type: str = "node"):
    import inquirer

    while True:
        databases = sorted(set([node.database for node in nodes.values()]))
        database_options = [
            inquirer.List("database", message="Select database", choices=databases)
        ]
        database = inquirer.prompt(database_options)["database"]
        nodes_filtered = {
            node_name: node
            for node_name, node in nodes.items()
            if node.database == database
        }

        schemas = sorted(set([node.schema for node in nodes_filtered.values()]))
        schema_options = [
            inquirer.List("schema", message="Select schema", choices=schemas)
        ]
        schema = inquirer.prompt(schema_options)["schema"]
        nodes_filtered = {
            node_name: node
            for node_name, node in nodes_filtered.items()
            if node.schema == schema
        }

        node_options = [
            inquirer.List(
                "node", message="Select node", choices=sorted(nodes_filtered.values())
            )
        ]
        node = inquirer.prompt(node_options)["node"]
        click.echo(f"{node.name} columns:")
        for column in node.columns.values():
            click.echo(f"- {column}")
        click.echo("")
        for stats in node.stats.values():
            if stats.id == "has_stats":
                continue
            click.echo(stats)
        if not click.confirm(f"Explore another {node_type}?"):
            break


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
                choices=["sources", "nodes"],
            )
        ]
        attribute = inquirer.prompt(attribute_options)["attribute"]

        if attribute == "nodes":
            explore_nodes(nodes)
        elif attribute == "sources":
            explore_nodes(catalog.sources, node_type="source")
        if not click.confirm("Explore another attribute?"):
            break
