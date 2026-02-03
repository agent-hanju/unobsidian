"""Tag extraction from markdown content."""

import re

# Tag pattern: #TagName (Obsidian-compatible, Unicode-aware)
# - Must start with # followed by a letter (any script) or underscore
# - Can contain letters, numbers, underscore, hyphen, forward slash
# - Supports Korean, CJK, Cyrillic, and other Unicode letters
# - Must be preceded by whitespace or start of string
TAG_PATTERN = re.compile(r"(?:^|(?<=\s))#([^\W\d][\w/\-]*)", re.UNICODE)


def expand_nested_tag(tag: str) -> list[str]:
    """Expand a nested tag into all ancestor tags.

    For example, "a/b/c" expands to ["a", "a/b", "a/b/c"].
    A simple tag like "project" returns ["project"].

    Args:
        tag: Tag string (without # prefix).

    Returns:
        List of expanded tags from root to full path.
    """
    parts = tag.split("/")
    expanded: list[str] = []
    for i in range(1, len(parts) + 1):
        expanded.append("/".join(parts[:i]))
    return expanded


def extract_tags(content: str) -> list[str]:
    """Extract tags from markdown content with nested tag expansion.

    Note: Content should have code blocks removed before calling this function.

    Tag rules (Obsidian-compatible):
    - Must start with # followed by a letter (any script, including Korean/CJK) or underscore
    - Can contain: letters, numbers, underscore (_), hyphen (-), forward slash (/)
    - Forward slash enables nested tags like #parent/child
    - Must be preceded by whitespace or be at start of line
    - Purely numeric tags like #123 are not recognized

    Nested tag expansion:
    - #parent/child expands to both "parent" and "parent/child"
    - #a/b/c expands to "a", "a/b", and "a/b/c"

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of tag strings without # prefix (deduplicated, order preserved).
    """
    seen: set[str] = set()
    result: list[str] = []

    for match in TAG_PATTERN.finditer(content):
        tag = match.group(1)
        for expanded in expand_nested_tag(tag):
            if expanded not in seen:
                seen.add(expanded)
                result.append(expanded)

    return result
