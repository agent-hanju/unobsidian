"""Graph builder - constructs knowledge graph from parsed markdown files."""

from pathlib import Path

from markgraph_mcp.graph.models import Graph, Node, Link
from markgraph_mcp.parser.engine import parse_markdown_file, ParseResult


def build_graph_from_results(results: list[ParseResult]) -> Graph:
    """Build a graph from parsing results.

    Args:
        results: List of ParseResult from parsing markdown files.

    Returns:
        Graph with nodes and links.
    """
    nodes: dict[str, Node] = {}
    links: list[Link] = []

    for result in results:
        # Create file node
        file_id = result.file_id
        if file_id not in nodes:
            nodes[file_id] = Node(
                id=file_id,
                type="file",
                label=file_id,
                metadata=result.frontmatter,
            )
        else:
            # Update metadata if file was referenced before being parsed
            nodes[file_id].metadata.update(result.frontmatter)
            nodes[file_id].type = "file"

        # Process wikilinks
        for target in result.wikilinks:
            # Create target node if not exists
            if target not in nodes:
                nodes[target] = Node(
                    id=target,
                    type="file",
                    label=target,
                )
            # Create link
            links.append(Link(
                source=file_id,
                target=target,
                relation="wikilink",
            ))

        # Process embeds
        for target in result.embeds:
            if target not in nodes:
                nodes[target] = Node(
                    id=target,
                    type="file",
                    label=target,
                )
            links.append(Link(
                source=file_id,
                target=target,
                relation="embed",
            ))

        # Process tags
        for tag in result.tags:
            tag_id = f"#{tag}"
            if tag_id not in nodes:
                nodes[tag_id] = Node(
                    id=tag_id,
                    type="tag",
                    label=tag,
                )
            links.append(Link(
                source=file_id,
                target=tag_id,
                relation="tag",
            ))

    return Graph(
        nodes=list(nodes.values()),
        links=links,
    )


def build_graph_from_directory(directory: Path, recursive: bool = True) -> Graph:
    """Build a graph from all markdown files in a directory.

    Args:
        directory: Path to the directory.
        recursive: If True, search subdirectories recursively.

    Returns:
        Graph with nodes and links.

    Raises:
        FileNotFoundError: If directory does not exist.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    pattern = "**/*.md" if recursive else "*.md"
    md_files = list(directory.glob(pattern))

    results: list[ParseResult] = []
    for file_path in md_files:
        try:
            result = parse_markdown_file(file_path)
            results.append(result)
        except (UnicodeDecodeError, OSError):
            # Skip files that cannot be read
            continue

    return build_graph_from_results(results)


def build_graph_from_paths(paths: list[str]) -> Graph:
    """Build a graph from multiple paths (files or directories).

    Args:
        paths: List of file or directory paths.

    Returns:
        Combined graph from all paths.
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

    return build_graph_from_results(all_results)
