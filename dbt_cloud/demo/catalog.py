import click
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dbt_cloud.command.command import ClickBaseModel


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
    SOURCE = "source"
    NODE = "node"


class CatalogExploreCommand(ClickBaseModel):
    """An inteactive application for exploring catalog artifacts."""

    file: Path = Field(default="catalog.json", description="Catalog file path.")
    title: str = Field(
        default="Data Catalog", description="ASCII art title for the app."
    )
    title_font: str = Field(
        default="rand-large",
        description="ASCII art title font (see https://github.com/sepandhaghighi/art#try-art-in-your-browser for a list of available fonts)",
    )

    def get_catalog(self) -> Catalog:
        return Catalog.parse_file(self.file)

    def print_title(self):
        from art import tprint

        tprint(self.title, font=self.title_font)

    def execute(self):
        import inquirer

        self.print_title()

        while True:
            node_type_options = [
                inquirer.List(
                    "node_type",
                    message="Select node type to explore",
                    choices=[node_type.value for node_type in NodeType],
                )
            ]
            node_type = NodeType(inquirer.prompt(node_type_options)["node_type"])
            self.explore(node_type=node_type)
            if not click.confirm("Explore another node type?"):
                break

    def explore(self, node_type: NodeType):
        """Interactive exploration of nodes to explore and display their metadata"""
        import inquirer

        catalog = self.get_catalog()
        if node_type == NodeType.SOURCE:
            nodes = list(catalog.sources.values())
        else:
            nodes = list(catalog.nodes.values())

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
