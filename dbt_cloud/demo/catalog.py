import click
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from dbt_cloud.command.command import DbtCloudBaseModel


class Stats(BaseModel):
    """Represent node stats in the Catalog."""

    id: str
    label: str
    value: Any
    include: bool
    description: str

    def __str__(self):
        return f"{self.label}: {self.value}"


class Column(BaseModel):
    """Represents a column in the Catalog."""

    type: str
    index: int
    name: str
    comment: Optional[str]

    def __str__(self):
        return f"{self.name} (type: {self.type}, index: {self.index}, comment: {self.comment})"


class Node(BaseModel):
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

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f"{self.name} (type: {self.type}, schema: {self.schema}, database: {self.database})"


class Catalog(BaseModel):
    """Represents a dbt catalog.json artifact."""

    metadata: Dict
    nodes: Dict[str, Node]
    sources: Dict[str, Node]
    errors: Optional[Dict]


class NodeType(Enum):
    NODE = "node"
    SOURCE = "source"


class CatalogExploreCommand(DbtCloudBaseModel):
    """An inteactive application for exploring catalog artifacts."""

    file: Path = Field(default="catalog.json", description="Catalog file path.")

    def get_catalog(self) -> Catalog:
        return Catalog.parse_file(self.file)

    def execute(self):
        import inquirer
        from art import tprint

        catalog = self.get_catalog()
        nodes = list(catalog.nodes.values())
        sources = list(catalog.sources.values())
        tprint("Data Catalog", font="rand-large")
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
                self.explore_nodes(nodes)
            elif attribute == "sources":
                self.explore_nodes(sources, node_type=NodeType.SOURCE)
            if not click.confirm("Explore another attribute?"):
                break

    @classmethod
    def explore_nodes(cls, nodes: List[Node], node_type: NodeType = NodeType.NODE):
        """Interactive exploration of nodes or sources to explore and display their metadata"""
        import inquirer

        while True:
            databases = sorted(set(map(lambda x: x.database, nodes)))
            database_options = [
                inquirer.List("database", message="Select database", choices=databases)
            ]
            database = inquirer.prompt(database_options)["database"]
            nodes_filtered = list(filter(lambda x: x.database == database, nodes))

            schemas = sorted(set(map(lambda x: x.schema, nodes_filtered)))
            schema_options = [
                inquirer.List("schema", message="Select schema", choices=schemas)
            ]
            schema = inquirer.prompt(schema_options)["schema"]
            nodes_filtered = list(filter(lambda x: x.schema == schema, nodes_filtered))

            node_options = [
                inquirer.List(
                    "node", message="Select node", choices=sorted(nodes_filtered)
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
            if not click.confirm(f"Explore another {node_type.value}?"):
                break


@click.command(help=CatalogExploreCommand.get_description())
@CatalogExploreCommand.click_options
def data_catalog(**kwargs):
    command = CatalogExploreCommand.from_click_options(**kwargs)
    command.execute()
