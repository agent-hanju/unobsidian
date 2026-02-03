"""Tests for graph builder."""

from pathlib import Path

import pytest

from markgraph_mcp.graph.builder import (
    build_graph_from_results,
    build_graph_from_directory,
    build_graph_from_paths,
)
from markgraph_mcp.parser.engine import ParseResult


class TestBuildGraphFromResults:
    """Tests for build_graph_from_results function."""

    def test_single_file(self):
        """Test building graph from single file result."""
        results = [
            ParseResult(
                file_id="NoteA",
                frontmatter={"title": "Note A"},
                wikilinks=["NoteB"],
                embeds=[],
                tags=["tag1"],
            )
        ]

        graph = build_graph_from_results(results)

        # Should have 3 nodes: NoteA, NoteB, #tag1
        assert len(graph.nodes) == 3

        # Find nodes by id
        node_ids = {n.id for n in graph.nodes}
        assert node_ids == {"NoteA", "NoteB", "#tag1"}

        # Check links: 1 wikilink + 1 tag
        assert len(graph.links) == 2

    def test_multiple_files_with_connections(self):
        """Test building graph from multiple connected files."""
        results = [
            ParseResult(
                file_id="A",
                wikilinks=["B"],
                embeds=[],
                tags=["shared"],
            ),
            ParseResult(
                file_id="B",
                wikilinks=["A"],
                embeds=[],
                tags=["shared"],
            ),
        ]

        graph = build_graph_from_results(results)

        # Should have 3 nodes: A, B, #shared
        assert len(graph.nodes) == 3

        # Should have 4 links: A->B, B->A, A->#shared, B->#shared
        assert len(graph.links) == 4

    def test_empty_results(self):
        """Test building graph from empty results."""
        graph = build_graph_from_results([])

        assert len(graph.nodes) == 0
        assert len(graph.links) == 0

    def test_nested_tag_creates_parent_child_links(self):
        """Test that nested tags create parent tag nodes and parent links."""
        results = [
            ParseResult(
                file_id="Note",
                wikilinks=[],
                embeds=[],
                tags=["project/frontend"],
            )
        ]

        graph = build_graph_from_results(results)

        node_ids = {n.id for n in graph.nodes}
        # Note + #project/frontend (direct tag) + #project (parent)
        assert node_ids == {"Note", "#project/frontend", "#project"}

        # Links: Note->#project/frontend (tag) + #project->#project/frontend (parent)
        assert len(graph.links) == 2

        tag_links = [l for l in graph.links if l.relation == "tag"]
        parent_links = [l for l in graph.links if l.relation == "parent"]
        assert len(tag_links) == 1
        assert tag_links[0].source == "Note"
        assert tag_links[0].target == "#project/frontend"
        assert len(parent_links) == 1
        assert parent_links[0].source == "#project"
        assert parent_links[0].target == "#project/frontend"

    def test_deeply_nested_tag_creates_full_hierarchy(self):
        """Test that a/b/c creates the full parent chain."""
        results = [
            ParseResult(
                file_id="Note",
                wikilinks=[],
                embeds=[],
                tags=["a/b/c"],
            )
        ]

        graph = build_graph_from_results(results)

        node_ids = {n.id for n in graph.nodes}
        assert node_ids == {"Note", "#a", "#a/b", "#a/b/c"}

        parent_links = [l for l in graph.links if l.relation == "parent"]
        parent_pairs = {(l.source, l.target) for l in parent_links}
        assert ("#a", "#a/b") in parent_pairs
        assert ("#a/b", "#a/b/c") in parent_pairs

    def test_parent_links_deduplicated(self):
        """Test that parent links are not duplicated across files."""
        results = [
            ParseResult(file_id="A", wikilinks=[], embeds=[], tags=["dev/python"]),
            ParseResult(file_id="B", wikilinks=[], embeds=[], tags=["dev/rust"]),
        ]

        graph = build_graph_from_results(results)

        parent_links = [l for l in graph.links if l.relation == "parent"]
        # #dev->#dev/python and #dev->#dev/rust (not duplicated #dev parent)
        assert len(parent_links) == 2

    def test_file_not_linked_to_parent_tag(self):
        """Test that file is only linked to the tag it mentions, not ancestor tags."""
        results = [
            ParseResult(
                file_id="Note",
                wikilinks=[],
                embeds=[],
                tags=["project/frontend"],
            )
        ]

        graph = build_graph_from_results(results)

        tag_links = [l for l in graph.links if l.relation == "tag"]
        # Only Note -> #project/frontend, NOT Note -> #project
        assert len(tag_links) == 1
        assert tag_links[0].target == "#project/frontend"


class TestBuildGraphFromDirectory:
    """Tests for build_graph_from_directory function."""

    def test_build_from_sample_vault(self, sample_vault: Path):
        """Test building graph from sample vault."""
        graph = build_graph_from_directory(sample_vault)

        # Should have file nodes
        file_nodes = [n for n in graph.nodes if n.type == "file"]
        assert len(file_nodes) >= 3  # DailyNote, ProjectA, ProjectB

        # Should have tag nodes
        tag_nodes = [n for n in graph.nodes if n.type == "tag"]
        assert len(tag_nodes) > 0

        # Should have links
        assert len(graph.links) > 0

    def test_directory_not_found(self, tmp_path: Path):
        """Test error when directory doesn't exist."""
        with pytest.raises(FileNotFoundError):
            build_graph_from_directory(tmp_path / "nonexistent")


class TestBuildGraphFromPaths:
    """Tests for build_graph_from_paths function."""

    def test_build_from_multiple_paths(self, sample_vault: Path):
        """Test building graph from multiple paths."""
        paths = [
            str(sample_vault / "DailyNote.md"),
            str(sample_vault / "ProjectA.md"),
        ]

        graph = build_graph_from_paths(paths)

        # Should have nodes from both files
        node_ids = {n.id for n in graph.nodes}
        assert "DailyNote" in node_ids
        assert "ProjectA" in node_ids

    def test_nonexistent_path_ignored(self, sample_vault: Path):
        """Test that nonexistent paths are ignored."""
        paths = [
            str(sample_vault / "DailyNote.md"),
            "/nonexistent/path.md",
        ]

        graph = build_graph_from_paths(paths)

        # Should still have nodes from valid file
        node_ids = {n.id for n in graph.nodes}
        assert "DailyNote" in node_ids
