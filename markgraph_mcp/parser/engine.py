"""Parsing orchestrator - combines all parsing modules."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from markgraph_mcp.parser.frontmatter import extract_frontmatter
from markgraph_mcp.parser.wikilinks import extract_wikilinks_as_strings
from markgraph_mcp.parser.tags import extract_tags
from markgraph_mcp.parser.embeds import extract_embeds_as_strings


def _empty_dict() -> dict[str, Any]:
    return {}


def _empty_list() -> list[str]:
    return []


@dataclass
class ParseResult:
    """Result of parsing a markdown file."""

    file_id: str
    frontmatter: dict[str, Any] = field(default_factory=_empty_dict)
    wikilinks: list[str] = field(default_factory=_empty_list)
    embeds: list[str] = field(default_factory=_empty_list)
    tags: list[str] = field(default_factory=_empty_list)


# Pattern to match fenced code blocks (``` or ~~~)
CODE_FENCE_PATTERN = re.compile(r"^(`{3,}|~{3,}).*?^\1", re.MULTILINE | re.DOTALL)

# Pattern to match inline code
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")


def _remove_code_blocks(content: str) -> str:
    """Remove code fences and inline code from content.

    This prevents parsing links/tags inside code blocks.

    Args:
        content: Markdown content.

    Returns:
        Content with code blocks replaced by empty strings.
    """
    # Remove fenced code blocks first (they may contain backticks)
    content = CODE_FENCE_PATTERN.sub("", content)
    # Remove inline code
    content = INLINE_CODE_PATTERN.sub("", content)
    return content


def parse_markdown_content(content: str, file_id: str) -> ParseResult:
    """Parse markdown content and extract all elements.

    Parsing order:
    1. Extract frontmatter (separate handling)
    2. Remove code blocks from remaining content
    3. Extract wikilinks, embeds, tags

    Args:
        content: Raw markdown content.
        file_id: Identifier for the file (usually filename without extension).

    Returns:
        ParseResult containing all extracted elements.
    """
    # Step 1: Extract frontmatter
    frontmatter_data: dict[str, Any]
    body: str
    frontmatter_data, body = extract_frontmatter(content)

    # Step 2: Remove code blocks
    clean_body = _remove_code_blocks(body)

    # Step 3: Extract elements
    wikilinks: list[str] = extract_wikilinks_as_strings(clean_body)
    embeds: list[str] = extract_embeds_as_strings(clean_body)
    tags: list[str] = extract_tags(clean_body)

    return ParseResult(
        file_id=file_id,
        frontmatter=frontmatter_data,
        wikilinks=wikilinks,
        embeds=embeds,
        tags=tags,
    )


def parse_markdown_file(file_path: Path) -> ParseResult:
    """Parse a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        ParseResult containing all extracted elements.

    Raises:
        FileNotFoundError: If file does not exist.
        UnicodeDecodeError: If file cannot be decoded as UTF-8.
    """
    content = file_path.read_text(encoding="utf-8")
    file_id = file_path.stem  # filename without extension
    return parse_markdown_content(content, file_id)
