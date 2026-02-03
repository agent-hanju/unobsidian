"""Tag-based document search operations."""

from pathlib import Path

from markgraph_mcp.parser.engine import parse_markdown_file, ParseResult
from markgraph_mcp.parser.tags import expand_nested_tag


def collect_results_from_paths(paths: list[str]) -> list[ParseResult]:
    """Collect parse results from multiple paths (files or directories).

    Args:
        paths: List of file or directory paths.

    Returns:
        List of ParseResult from all valid markdown files.
    """
    all_results: list[ParseResult] = []

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            continue

        if path.is_file() and path.suffix == ".md":
            try:
                result = parse_markdown_file(path)
                all_results.append(result)
            except (UnicodeDecodeError, OSError):
                continue
        elif path.is_dir():
            for md_file in path.glob("**/*.md"):
                try:
                    result = parse_markdown_file(md_file)
                    all_results.append(result)
                except (UnicodeDecodeError, OSError):
                    continue

    return all_results


def search_by_tag(paths: list[str], tag: str) -> list[dict[str, object]]:
    """Search for documents that contain a specific tag.

    Supports nested tag matching: searching for "project" will match documents
    tagged with #project/frontend, #project/backend, etc., because each
    document's tags are expanded to include ancestor tags during search.

    For example, a document with #project/frontend matches searches for
    both "project" and "project/frontend".

    Args:
        paths: List of file or directory paths to search.
        tag: Tag to search for (without # prefix).

    Returns:
        List of dicts with file_id and all tags for each matching document.
    """
    results = collect_results_from_paths(paths)
    matches: list[dict[str, object]] = []

    for result in results:
        # Expand each original tag to include ancestors for matching
        all_expanded: set[str] = set()
        for t in result.tags:
            all_expanded.update(expand_nested_tag(t))

        if tag in all_expanded:
            matches.append({
                "file_id": result.file_id,
                "tags": result.tags,
            })

    return matches
