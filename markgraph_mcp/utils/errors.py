"""Custom exceptions for MarkGraph."""


class MarkGraphError(Exception):
    """Base exception for MarkGraph errors."""

    pass


class ParseError(MarkGraphError):
    """Error during markdown parsing."""

    pass



class GraphError(MarkGraphError):
    """Error during graph operations."""

    pass


class NodeNotFoundError(GraphError):
    """Node not found in graph."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(f"Node not found: {node_id}")
