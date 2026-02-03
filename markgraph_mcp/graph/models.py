"""Graph data models - D3.js compatible format."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Node(BaseModel):
    """A node in the knowledge graph.

    Represents a markdown file.
    """
    id: str
    type: Literal["file"] = "file"
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Link(BaseModel):
    """A link (edge) between nodes.

    Represents wikilinks or embeds between files.
    """
    source: str
    target: str
    relation: Literal["wikilink", "embed"]
    metadata: dict[str, Any] = Field(default_factory=dict)


class Graph(BaseModel):
    """Knowledge graph in D3.js compatible format.

    Can be directly used with d3.forceSimulation().
    """
    nodes: list[Node] = Field(default_factory=lambda: list[Node]())
    links: list[Link] = Field(default_factory=lambda: list[Link]())
