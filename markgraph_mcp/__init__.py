"""MarkGraph MCP Server - Knowledge graph extraction from markdown files."""

__version__ = "0.1.0"

from markgraph_mcp.graph import Graph, Node, Link
from markgraph_mcp.server import mcp

__all__ = [
    "__version__",
    "Graph",
    "Node",
    "Link",
    "mcp",
]
