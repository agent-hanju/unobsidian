"""Tests for tag parsing."""

import pytest

from markgraph_mcp.parser.tags import extract_tags, expand_nested_tag


class TestExtractTags:
    """Tests for extract_tags function."""

    def test_simple_tag(self):
        """Test parsing simple tags."""
        content = "Note with #project tag."
        tags = extract_tags(content)

        assert tags == ["project"]

    def test_multiple_tags(self):
        """Test parsing multiple tags."""
        content = "#tagA #tagB #tagC"
        tags = extract_tags(content)

        assert tags == ["tagA", "tagB", "tagC"]

    def test_nested_tag(self):
        """Test parsing nested/hierarchical tags with expansion."""
        content = "Has #project/frontend tag"
        tags = extract_tags(content)

        # Nested tags expand: #project/frontend -> ["project", "project/frontend"]
        assert tags == ["project", "project/frontend"]

    def test_tag_with_numbers(self):
        """Test tags with numbers (not starting with number)."""
        content = "#tag123 and #v2"
        tags = extract_tags(content)

        assert tags == ["tag123", "v2"]

    def test_tag_with_underscore(self):
        """Test tags with underscores."""
        content = "#my_tag and #another_tag_here"
        tags = extract_tags(content)

        assert tags == ["my_tag", "another_tag_here"]

    def test_tag_with_hyphen(self):
        """Test tags with hyphens."""
        content = "#my-tag and #kebab-case-tag"
        tags = extract_tags(content)

        assert tags == ["my-tag", "kebab-case-tag"]

    def test_tag_at_line_start(self):
        """Test tag at the start of a line."""
        content = "#firstTag\nSome text"
        tags = extract_tags(content)

        assert tags == ["firstTag"]

    def test_no_tag_after_word(self):
        """Test that # after a word is not a tag."""
        content = "word#notAtag"
        tags = extract_tags(content)

        assert tags == []

    def test_deduplication(self):
        """Test that duplicate tags are removed."""
        content = "#tag #tag #tag"
        tags = extract_tags(content)

        assert tags == ["tag"]

    def test_korean_tag(self):
        """Test parsing Korean tags."""
        content = "#프로젝트 #일기 #할일"
        tags = extract_tags(content)

        assert tags == ["프로젝트", "일기", "할일"]

    def test_mixed_unicode_tag(self):
        """Test parsing mixed Korean and ASCII tags."""
        content = "#project #프로젝트/프론트엔드 #日本語"
        tags = extract_tags(content)

        # #프로젝트/프론트엔드 expands to 프로젝트 and 프로젝트/프론트엔드
        assert tags == ["project", "프로젝트", "프로젝트/프론트엔드", "日本語"]

    def test_numeric_only_tag_ignored(self):
        """Test that purely numeric tags are ignored."""
        content = "#123 #456"
        tags = extract_tags(content)

        assert tags == []

    def test_empty_content(self):
        """Test with empty content."""
        tags = extract_tags("")
        assert tags == []

    def test_deeply_nested_tag(self):
        """Test deeply nested tag expansion."""
        content = "#a/b/c/d"
        tags = extract_tags(content)

        assert tags == ["a", "a/b", "a/b/c", "a/b/c/d"]

    def test_nested_tag_deduplication(self):
        """Test that parent tags from expansion are deduplicated."""
        content = "#project/frontend #project/backend"
        tags = extract_tags(content)

        # "project" appears from both expansions but is deduplicated
        assert tags == ["project", "project/frontend", "project/backend"]

    def test_nested_with_explicit_parent(self):
        """Test nested tag when parent is also explicitly used."""
        content = "#project #project/frontend"
        tags = extract_tags(content)

        # "project" from explicit tag, then "project/frontend" from nested
        # "project" is already seen so not duplicated
        assert tags == ["project", "project/frontend"]


class TestExpandNestedTag:
    """Tests for expand_nested_tag function."""

    def test_simple_tag(self):
        """Test that simple tag returns itself."""
        assert expand_nested_tag("project") == ["project"]

    def test_two_level(self):
        """Test two-level nested tag."""
        assert expand_nested_tag("project/frontend") == ["project", "project/frontend"]

    def test_three_level(self):
        """Test three-level nested tag."""
        assert expand_nested_tag("a/b/c") == ["a", "a/b", "a/b/c"]

    def test_four_level(self):
        """Test four-level nested tag."""
        assert expand_nested_tag("a/b/c/d") == ["a", "a/b", "a/b/c", "a/b/c/d"]
