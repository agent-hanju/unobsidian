"""Tests for graph models."""

import pytest

from markgraph_mcp.graph.models import Node, Link, Graph


class TestNode:
    """Tests for Node model."""

    def test_file_node(self):
        """Test creating a file node."""
        node = Node(id="MyNote", type="file", label="My Note")

        assert node.id == "MyNote"
        assert node.type == "file"
        assert node.label == "My Note"
        assert node.metadata == {}

    def test_tag_node(self):
        """Test creating a tag node."""
        node = Node(id="#project", type="tag", label="project")

        assert node.id == "#project"
        assert node.type == "tag"

    def test_node_with_metadata(self):
        """Test node with metadata."""
        metadata = {"status": "active", "priority": 1}
        node = Node(id="Note", type="file", metadata=metadata)

        assert node.metadata == metadata

    def test_node_serialization(self):
        """Test node JSON serialization."""
        node = Node(id="Note", type="file", label="Note")
        data = node.model_dump()

        assert data["id"] == "Note"
        assert data["type"] == "file"
        assert data["label"] == "Note"


class TestLink:
    """Tests for Link model."""

    def test_wikilink(self):
        """Test creating a wikilink."""
        link = Link(source="A", target="B", relation="wikilink")

        assert link.source == "A"
        assert link.target == "B"
        assert link.relation == "wikilink"

    def test_embed_link(self):
        """Test creating an embed link."""
        link = Link(source="Note", target="image.png", relation="embed")

        assert link.relation == "embed"

    def test_tag_link(self):
        """Test creating a tag link."""
        link = Link(source="Note", target="#tag", relation="tag")

        assert link.relation == "tag"

    def test_parent_link(self):
        """Test creating a parent link for nested tag hierarchy."""
        link = Link(source="#project", target="#project/frontend", relation="parent")

        assert link.relation == "parent"
        assert link.source == "#project"
        assert link.target == "#project/frontend"


class TestGraph:
    """Tests for Graph model."""

    def test_empty_graph(self):
        """Test creating empty graph."""
        graph = Graph()

        assert graph.nodes == []
        assert graph.links == []

    def test_graph_with_data(self):
        """Test creating graph with nodes and links."""
        nodes = [
            Node(id="A", type="file"),
            Node(id="B", type="file"),
        ]
        links = [
            Link(source="A", target="B", relation="wikilink"),
        ]
        graph = Graph(nodes=nodes, links=links)

        assert len(graph.nodes) == 2
        assert len(graph.links) == 1

    def test_d3_compatible_output(self):
        """Test that output is D3.js compatible."""
        nodes = [Node(id="A", type="file")]
        links = [Link(source="A", target="B", relation="wikilink")]
        graph = Graph(nodes=nodes, links=links)

        data = graph.model_dump()

        # D3.js expects 'nodes' and 'links' (not 'edges')
        assert "nodes" in data
        assert "links" in data
        assert "edges" not in data
