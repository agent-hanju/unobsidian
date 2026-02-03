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

        # Check links
        assert len(graph.links) == 2  # wikilink + tag

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
