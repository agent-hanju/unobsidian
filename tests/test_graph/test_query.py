"""Tests for graph query operations."""

import pytest

from markgraph_mcp.graph.models import Graph, Node, Link
from markgraph_mcp.graph.query import query_neighbors, get_node_by_id, get_links_for_node


@pytest.fixture
def sample_graph() -> Graph:
    """Create a sample graph for testing (file nodes only, no tag nodes)."""
    nodes = [
        Node(id="A", type="file", label="Node A"),
        Node(id="B", type="file", label="Node B"),
        Node(id="C", type="file", label="Node C"),
        Node(id="D", type="file", label="Node D"),
        Node(id="E", type="file", label="Node E"),
    ]
    links = [
        Link(source="A", target="B", relation="wikilink"),
        Link(source="B", target="C", relation="wikilink"),
        Link(source="C", target="D", relation="wikilink"),
        Link(source="A", target="E", relation="embed"),
    ]
    return Graph(nodes=nodes, links=links)


class TestQueryNeighbors:
    """Tests for query_neighbors function."""

    def test_depth_1(self, sample_graph: Graph):
        """Test querying with depth 1."""
        result = query_neighbors(sample_graph, "A", depth=1)

        node_ids = {n.id for n in result.nodes}
        # A and its direct neighbors: B, E
        assert "A" in node_ids
        assert "B" in node_ids
        assert "E" in node_ids
        assert "C" not in node_ids  # C is 2 hops away

    def test_depth_2(self, sample_graph: Graph):
        """Test querying with depth 2."""
        result = query_neighbors(sample_graph, "A", depth=2)

        node_ids = {n.id for n in result.nodes}
        # A, B, E, C (C is now included via A->B->C)
        assert "A" in node_ids
        assert "B" in node_ids
        assert "C" in node_ids
        assert "E" in node_ids

    def test_depth_clamped(self, sample_graph: Graph):
        """Test that depth is clamped to 1-3."""
        # Depth 0 should be treated as 1
        result = query_neighbors(sample_graph, "A", depth=0)
        assert len(result.nodes) > 1

        # Depth > 3 should be treated as 3
        result = query_neighbors(sample_graph, "A", depth=10)
        assert len(result.nodes) == len(sample_graph.nodes)  # All reachable

    def test_nonexistent_node(self, sample_graph: Graph):
        """Test querying for nonexistent node."""
        result = query_neighbors(sample_graph, "NonExistent", depth=1)

        assert len(result.nodes) == 0
        assert len(result.links) == 0

    def test_bidirectional_traversal(self, sample_graph: Graph):
        """Test that traversal works in both directions."""
        # Starting from C, should find B (reverse of B->C link)
        result = query_neighbors(sample_graph, "C", depth=1)

        node_ids = {n.id for n in result.nodes}
        assert "B" in node_ids
        assert "D" in node_ids


class TestGetNodeById:
    """Tests for get_node_by_id function."""

    def test_existing_node(self, sample_graph: Graph):
        """Test finding existing node."""
        node = get_node_by_id(sample_graph, "A")

        assert node is not None
        assert node.id == "A"
        assert node.label == "Node A"

    def test_nonexistent_node(self, sample_graph: Graph):
        """Test finding nonexistent node."""
        node = get_node_by_id(sample_graph, "X")
        assert node is None


class TestGetLinksForNode:
    """Tests for get_links_for_node function."""

    def test_get_links(self, sample_graph: Graph):
        """Test getting links for a node."""
        links = get_links_for_node(sample_graph, "A")

        # A has 2 links: A->B (wikilink) and A->E (embed)
        assert len(links) == 2

    def test_node_as_target(self, sample_graph: Graph):
        """Test getting links where node is target."""
        links = get_links_for_node(sample_graph, "B")

        # B is source in B->C and target in A->B
        assert len(links) == 2
