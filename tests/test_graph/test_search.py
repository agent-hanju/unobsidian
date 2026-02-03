"""Tests for tag-based document search."""

from pathlib import Path

import pytest

from markgraph_mcp.graph.search import search_by_tag


class TestSearchByTag:
    """Tests for search_by_tag function."""

    def test_search_simple_tag(self, sample_vault: Path):
        """Test searching for a simple tag."""
        results = search_by_tag([str(sample_vault)], "daily")

        file_ids = [r["file_id"] for r in results]
        assert "DailyNote" in file_ids

    def test_search_shared_tag(self, sample_vault: Path):
        """Test searching for a tag shared across files."""
        results = search_by_tag([str(sample_vault)], "project")

        file_ids = [r["file_id"] for r in results]
        # ProjectA has #project and #project/frontend; search expands child tags
        assert "ProjectA" in file_ids

    def test_search_nested_tag_matches_parent(self, sample_vault: Path):
        """Test that searching parent tag finds files with nested child tags."""
        # ProjectA has #project/frontend; expand_nested_tag produces ["project", "project/frontend"]
        # So searching for "project" matches via expansion
        results = search_by_tag([str(sample_vault)], "project")

        file_ids = [r["file_id"] for r in results]
        assert "ProjectA" in file_ids

    def test_search_nested_tag_full_path(self, sample_vault: Path):
        """Test searching for full nested tag path."""
        results = search_by_tag([str(sample_vault)], "project/frontend")

        file_ids = [r["file_id"] for r in results]
        assert "ProjectA" in file_ids

    def test_search_nonexistent_tag(self, sample_vault: Path):
        """Test searching for a tag that doesn't exist."""
        results = search_by_tag([str(sample_vault)], "nonexistent")

        assert results == []

    def test_search_returns_tags_in_results(self, sample_vault: Path):
        """Test that search results include all tags for matched files."""
        results = search_by_tag([str(sample_vault)], "daily")

        daily_result = next(r for r in results if r["file_id"] == "DailyNote")
        assert "daily" in daily_result["tags"]
        assert "work" in daily_result["tags"]

    def test_search_with_file_path(self, sample_vault: Path):
        """Test searching with individual file path."""
        results = search_by_tag([str(sample_vault / "DailyNote.md")], "daily")

        assert len(results) == 1
        assert results[0]["file_id"] == "DailyNote"

    def test_search_nonexistent_path(self):
        """Test searching with nonexistent path."""
        results = search_by_tag(["/nonexistent/path"], "tag")

        assert results == []

    def test_search_with_tmp_files(self, tmp_path: Path):
        """Test search with custom temporary files."""
        # Create files with nested tags
        (tmp_path / "note1.md").write_text("#dev/python #dev/rust")
        (tmp_path / "note2.md").write_text("#dev/python")
        (tmp_path / "note3.md").write_text("#design")

        # Search for parent tag "dev" should match note1 and note2
        results = search_by_tag([str(tmp_path)], "dev")
        file_ids = {r["file_id"] for r in results}
        assert file_ids == {"note1", "note2"}

        # Search for specific nested tag
        results = search_by_tag([str(tmp_path)], "dev/rust")
        file_ids = {r["file_id"] for r in results}
        assert file_ids == {"note1"}

        # Search for "design" should only match note3
        results = search_by_tag([str(tmp_path)], "design")
        file_ids = {r["file_id"] for r in results}
        assert file_ids == {"note3"}
