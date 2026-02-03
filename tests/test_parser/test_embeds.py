"""Tests for embed parsing."""

import pytest

from markgraph_mcp.parser.embeds import extract_embeds, extract_embeds_as_strings


class TestExtractEmbeds:
    """Tests for extract_embeds function."""

    def test_simple_embed(self):
        """Test parsing simple embeds."""
        content = "Image: ![[image.png]]"
        embeds = extract_embeds(content)

        assert len(embeds) == 1
        assert embeds[0].target == "image.png"

    def test_multiple_embeds(self):
        """Test parsing multiple embeds."""
        content = "![[a.png]] and ![[b.svg]] and ![[c.pdf]]"
        embeds = extract_embeds(content)

        assert len(embeds) == 3
        assert [e.target for e in embeds] == ["a.png", "b.svg", "c.pdf"]

    def test_embed_vs_wikilink(self):
        """Test that embeds are distinguished from wikilinks."""
        content = "[[wikilink]] and ![[embed]]"
        embeds = extract_embeds(content)

        assert len(embeds) == 1
        assert embeds[0].target == "embed"

    def test_empty_content(self):
        """Test with empty content."""
        embeds = extract_embeds("")
        assert len(embeds) == 0


class TestExtractEmbedsAsStrings:
    """Tests for extract_embeds_as_strings function."""

    def test_deduplication(self):
        """Test that duplicate embeds are removed."""
        content = "![[img.png]] and ![[img.png]]"
        targets = extract_embeds_as_strings(content)

        assert targets == ["img.png"]
