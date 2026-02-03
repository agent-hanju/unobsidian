"""YAML frontmatter extraction."""

import re
from typing import Any

import frontmatter  # type: ignore[import-untyped]


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content.

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter).
        If no frontmatter exists, returns empty dict and original content.
    """
    try:
        post = frontmatter.loads(content)
        metadata: dict[str, Any] = dict(post.metadata)
        body: str = post.content
        return metadata, body
    except Exception:
        # If parsing fails, return empty metadata and original content
        return {}, content


def remove_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block from content.

    Args:
        content: Raw markdown content.

    Returns:
        Content with frontmatter removed.
    """
    # Match frontmatter at the start of the document
    pattern = r"^---\s*\n.*?\n---\s*\n?"
    return re.sub(pattern, "", content, count=1, flags=re.DOTALL)
