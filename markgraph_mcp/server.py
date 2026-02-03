"""MarkGraph MCP Server - Knowledge graph from Obsidian-style markdown."""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from markgraph_mcp.graph import build_graph_from_paths, query_neighbors

# Initialize MCP server
mcp = FastMCP("markgraph")


@mcp.tool()
def get_structure(
    paths: Annotated[
        list[str],
        Field(description="List of file or directory paths to parse. Directories are searched recursively for .md files."),
    ],
) -> dict[str, Any]:
    """Parse Obsidian-style markdown files and return a D3.js-compatible knowledge graph with nodes (files, tags) and links (wikilinks, embeds, tags)."""
    return build_graph_from_paths(paths).model_dump()


@mcp.tool()
def query_neighbors_tool(
    paths: Annotated[
        list[str],
        Field(description="List of file or directory paths to parse. Directories are searched recursively for .md files."),
    ],
    node_id: Annotated[
        str,
        Field(description="ID of the starting node (filename without .md, or #tagname)."),
    ],
    depth: Annotated[
        int,
        Field(default=1, description="BFS traversal depth (1-3). Higher values include more distant connections."),
    ] = 1,
) -> dict[str, Any]:
    """Parse markdown files, build the knowledge graph, and return a subgraph of the specified node's neighbors via BFS traversal."""
    full_graph = build_graph_from_paths(paths)
    return query_neighbors(full_graph, node_id, depth).model_dump()


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
