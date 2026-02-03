"""MarkGraph MCP Server - Knowledge graph from Obsidian-style markdown."""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from markgraph_mcp.graph import build_graph_from_paths, query_neighbors, search_by_tag

# Initialize MCP server
mcp = FastMCP("markgraph")


@mcp.tool()
def get_structure(
    paths: Annotated[
        list[str],
        Field(description="List of file or directory paths to parse. Directories are searched recursively for .md files."),
    ],
) -> dict[str, Any]:
    """Parse Obsidian-style markdown files and return a D3.js-compatible knowledge graph with nodes (files) and links (wikilinks, embeds)."""
    return build_graph_from_paths(paths).model_dump()


@mcp.tool()
def query_neighbors_tool(
    paths: Annotated[
        list[str],
        Field(description="List of file or directory paths to parse. Directories are searched recursively for .md files."),
    ],
    node_id: Annotated[
        str,
        Field(description="ID of the starting node (filename without .md extension)."),
    ],
    depth: Annotated[
        int,
        Field(default=1, description="BFS traversal depth (1-3). Higher values include more distant connections."),
    ] = 1,
) -> dict[str, Any]:
    """Parse markdown files, build the knowledge graph, and return a subgraph of the specified node's neighbors via BFS traversal."""
    full_graph = build_graph_from_paths(paths)
    return query_neighbors(full_graph, node_id, depth).model_dump()


@mcp.tool()
def search_by_tag_tool(
    paths: Annotated[
        list[str],
        Field(description="List of file or directory paths to search. Directories are searched recursively for .md files."),
    ],
    tag: Annotated[
        str,
        Field(description="Tag to search for (without # prefix). Supports nested tags: searching 'project' matches files with #project and #project/frontend."),
    ],
) -> list[dict[str, object]]:
    """Search for documents containing a specific tag. Nested tags like #parent/child belong to both 'parent' and 'parent/child', so searching for 'parent' returns documents tagged with #parent/child as well."""
    return search_by_tag(paths, tag)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
