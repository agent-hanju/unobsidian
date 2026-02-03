"""Tests for wikilink parsing."""

import pytest

from markgraph_mcp.parser.wikilinks import extract_wikilinks, extract_wikilinks_as_strings


class TestExtractWikilinks:
    """Tests for extract_wikilinks function."""

    def test_simple_wikilink(self):
        """Test parsing simple wikilinks."""
        content = "Link to [[Target]] here."
        links = extract_wikilinks(content)

        assert len(links) == 1
        assert links[0].target == "Target"

    def test_multiple_wikilinks(self):
        """Test parsing multiple wikilinks."""
        content = "Links: [[FileA]], [[FileB]], [[FileC]]"
        links = extract_wikilinks(content)

        assert len(links) == 3
        assert [l.target for l in links] == ["FileA", "FileB", "FileC"]

    def test_wikilink_with_alias(self):
        """Test parsing wikilinks with aliases."""
        content = "See [[Target|Display Name]] for more."
        links = extract_wikilinks(content)

        assert len(links) == 1
        assert links[0].target == "Target"

    def test_wikilink_with_spaces(self):
        """Test parsing wikilinks with spaces in target."""
        content = "Link to [[My Note Name]] here."
        links = extract_wikilinks(content)

        assert len(links) == 1
        assert links[0].target == "My Note Name"

    def test_empty_content(self):
        """Test with empty content."""
        links = extract_wikilinks("")
        assert len(links) == 0

    def test_no_wikilinks(self):
        """Test content without wikilinks."""
        content = "Just regular text without any links."
        links = extract_wikilinks(content)
        assert len(links) == 0


class TestExtractWikilinksAsStrings:
    """Tests for extract_wikilinks_as_strings function."""

    def test_deduplication(self):
        """Test that duplicate links are removed."""
        content = "[[Target]] and [[Target]] again [[Target]]"
        targets = extract_wikilinks_as_strings(content)

        assert targets == ["Target"]

    def test_order_preserved(self):
        """Test that order is preserved for unique links."""
        content = "[[A]] then [[B]] then [[C]]"
        targets = extract_wikilinks_as_strings(content)

        assert targets == ["A", "B", "C"]
