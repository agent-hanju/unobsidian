"""Embed extraction from markdown content."""

import re
from dataclasses import dataclass


@dataclass
class Embed:
    """Represents a parsed embed."""

    target: str


# Pattern: ![[Target]]
# Must have ! before [[ to distinguish from regular wikilinks
EMBED_PATTERN = re.compile(r"!\[\[([^\]]+)\]\]")


def extract_embeds(content: str) -> list[Embed]:
    """Extract embeds from markdown content.

    Note: Content should have code blocks removed before calling this function.

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of Embed objects.
    """
    embeds: list[Embed] = []
    for match in EMBED_PATTERN.finditer(content):
        target = match.group(1).strip()
        if target:
            embeds.append(Embed(target=target))
    return embeds


def extract_embeds_as_strings(content: str) -> list[str]:
    """Extract embed targets as strings.

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of embed target strings (deduplicated, order preserved).
    """
    seen: set[str] = set()
    result: list[str] = []
    for embed in extract_embeds(content):
        if embed.target not in seen:
            seen.add(embed.target)
            result.append(embed.target)
    return result
