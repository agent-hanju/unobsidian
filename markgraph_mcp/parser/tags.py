"""Tag extraction from markdown content."""

import re

# Tag pattern: #TagName (Obsidian-compatible, Unicode-aware)
# - Must start with # followed by a letter (any script) or underscore
# - Can contain letters, numbers, underscore, hyphen, forward slash
# - Supports Korean, CJK, Cyrillic, and other Unicode letters
# - Must be preceded by whitespace or start of string
TAG_PATTERN = re.compile(r"(?:^|(?<=\s))#([^\W\d][\w/\-]*)", re.UNICODE)


def extract_tags(content: str) -> list[str]:
    """Extract tags from markdown content.

    Note: Content should have code blocks removed before calling this function.

    Tag rules (Obsidian-compatible):
    - Must start with # followed by a letter (any script, including Korean/CJK) or underscore
    - Can contain: letters, numbers, underscore (_), hyphen (-), forward slash (/)
    - Forward slash enables nested tags like #parent/child
    - Must be preceded by whitespace or be at start of line
    - Purely numeric tags like #123 are not recognized

    Args:
        content: Markdown content with code blocks already removed.

    Returns:
        List of tag strings without # prefix (deduplicated, order preserved).
    """
    seen: set[str] = set()
    result: list[str] = []

    for match in TAG_PATTERN.finditer(content):
        tag = match.group(1)
        if tag not in seen:
            seen.add(tag)
            result.append(tag)

    return result
