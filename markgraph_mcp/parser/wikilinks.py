"""Wikilink extraction from markdown content."""

import re
from dataclasses import dataclass


@dataclass
class WikiLink:
    """Represents a parsed wikilink."""

    target: str
    alias: str | None = None


# Pattern: [[Target]] or [[Target|Alias]]
# Negative lookbehind (?<!!) excludes embeds (![[...]])
# Captures the target (before |) and ignores alias
WIKILINK_PATTERN = re.compile(r"(?<!!)\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def extract_wikilinks(content: str) -> list[WikiLink]:
    """Extract wikilinks from markdown content.

    Note: Content should have code blocks removed before calling this function.

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of WikiLink objects with target and optional alias.
    """
    links: list[WikiLink] = []
    for match in WIKILINK_PATTERN.finditer(content):
        target = match.group(1).strip()
        if target:
            links.append(WikiLink(target=target))
    return links


def extract_wikilinks_as_strings(content: str) -> list[str]:
    """Extract wikilink targets as strings.

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of wikilink target strings (deduplicated, order preserved).
    """
    seen: set[str] = set()
    result: list[str] = []
    for link in extract_wikilinks(content):
        if link.target not in seen:
            seen.add(link.target)
            result.append(link.target)
    return result
