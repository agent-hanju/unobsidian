"""Tests for parsing engine."""

import pytest

from markgraph_mcp.parser.engine import parse_markdown_content, parse_markdown_file


class TestParseMarkdownContent:
    """Tests for parse_markdown_content function."""

    def test_full_parsing(self, daily_note_content: str):
        """Test parsing content with all elements."""
        result = parse_markdown_content(daily_note_content, "DailyNote")

        assert result.file_id == "DailyNote"
        # frontmatter library parses dates as datetime.date objects
        assert result.frontmatter["author"] == "John"
        assert "date" in result.frontmatter
        assert set(result.wikilinks) == {"ProjectA", "ProjectB"}
        assert result.embeds == ["Screenshot.png"]
        assert set(result.tags) == {"daily", "work"}

    def test_code_block_exclusion(self, project_a_content: str):
        """Test that code blocks are excluded from parsing."""
        result = parse_markdown_content(project_a_content, "ProjectA")

        # Should NOT include links/tags from code blocks
        assert "NotALink" not in result.wikilinks
        assert "notAtag" not in result.tags
        assert "AlsoNotALink" not in result.wikilinks

        # Should include real links/tags
        assert "ProjectB" in result.wikilinks
        assert "DailyNote" in result.wikilinks
        assert "project" in result.tags
        assert "important" in result.tags
        # Nested tag #project/frontend expands to both "project" and "project/frontend"
        assert "project/frontend" in result.tags

    def test_empty_content(self):
        """Test parsing empty content."""
        result = parse_markdown_content("", "Empty")

        assert result.file_id == "Empty"
        assert result.frontmatter == {}
        assert result.wikilinks == []
        assert result.embeds == []
        assert result.tags == []


class TestParseMarkdownFile:
    """Tests for parse_markdown_file function."""

    def test_parse_file(self, daily_note_path):
        """Test parsing a real file."""
        result = parse_markdown_file(daily_note_path)

        assert result.file_id == "DailyNote"
        assert "ProjectA" in result.wikilinks
        assert "daily" in result.tags

    def test_file_not_found(self, tmp_path):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_markdown_file(tmp_path / "nonexistent.md")
