"""Graph data models - D3.js compatible format."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Node(BaseModel):
    """A node in the knowledge graph.

    Represents either a markdown file or a tag.
    """
    id: str
    type: Literal["file", "tag"]
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Link(BaseModel):
    """A link (edge) between nodes.

    Represents wikilinks, embeds, or tag relationships.
    """
    source: str
    target: str
    relation: Literal["wikilink", "embed", "tag"]
    metadata: dict[str, Any] = Field(default_factory=dict)


class Graph(BaseModel):
    """Knowledge graph in D3.js compatible format.

    Can be directly used with d3.forceSimulation().
    """
    nodes: list[Node] = Field(default_factory=lambda: list[Node]())
    links: list[Link] = Field(default_factory=lambda: list[Link]())
