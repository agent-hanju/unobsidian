"""Tests for frontmatter parsing."""

import pytest

from markgraph_mcp.parser.frontmatter import extract_frontmatter, remove_frontmatter


class TestExtractFrontmatter:
    """Tests for extract_frontmatter function."""

    def test_simple_frontmatter(self):
        """Test extracting simple frontmatter."""
        content = """---
title: My Note
author: John
---

# Content here
"""
        metadata, body = extract_frontmatter(content)

        assert metadata == {"title": "My Note", "author": "John"}
        assert "# Content here" in body
        assert "---" not in body

    def test_no_frontmatter(self):
        """Test content without frontmatter."""
        content = "# Just a heading\n\nSome content."
        metadata, body = extract_frontmatter(content)

        assert metadata == {}
        assert body == content

    def test_nested_frontmatter(self):
        """Test frontmatter with nested values."""
        content = """---
tags:
  - tag1
  - tag2
metadata:
  key: value
---

Body
"""
        metadata, body = extract_frontmatter(content)

        assert metadata["tags"] == ["tag1", "tag2"]
        assert metadata["metadata"] == {"key": "value"}


class TestRemoveFrontmatter:
    """Tests for remove_frontmatter function."""

    def test_remove_frontmatter(self):
        """Test removing frontmatter block."""
        content = """---
title: Test
---

# Content
"""
        result = remove_frontmatter(content)

        assert "---" not in result
        assert "title" not in result
        assert "# Content" in result

    def test_no_frontmatter_to_remove(self):
        """Test when there's no frontmatter."""
        content = "# Just content"
        result = remove_frontmatter(content)

        assert result == content
