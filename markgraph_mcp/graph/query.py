"""Graph query operations - BFS-based neighbor traversal."""

from collections import deque

from markgraph_mcp.graph.models import Graph, Node, Link


def query_neighbors(graph: Graph, node_id: str, depth: int = 1) -> Graph:
    """Query neighbors of a node up to specified depth using BFS.

    Args:
        graph: The full knowledge graph.
        node_id: ID of the starting node.
        depth: Maximum traversal depth (1-3, clamped).

    Returns:
        Subgraph containing the node and its neighbors up to depth.
        If node_id is not found, returns empty graph.
    """
    # Clamp depth to valid range
    depth = max(1, min(3, depth))

    # Build adjacency lists (bidirectional for undirected traversal)
    adjacency: dict[str, set[str]] = {}
    link_lookup: dict[tuple[str, str], Link] = {}

    for link in graph.links:
        # Forward direction
        if link.source not in adjacency:
            adjacency[link.source] = set()
        adjacency[link.source].add(link.target)
        link_lookup[(link.source, link.target)] = link

        # Reverse direction (for bidirectional traversal)
        if link.target not in adjacency:
            adjacency[link.target] = set()
        adjacency[link.target].add(link.source)
        # Store reverse lookup with original link
        if (link.target, link.source) not in link_lookup:
            link_lookup[(link.target, link.source)] = link

    # Build node lookup
    node_lookup: dict[str, Node] = {node.id: node for node in graph.nodes}

    # Check if starting node exists
    if node_id not in node_lookup:
        return Graph()

    # BFS traversal
    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(node_id, 0)])
    visited.add(node_id)

    result_nodes: dict[str, Node] = {}
    result_links: list[Link] = []
    seen_links: set[tuple[str, str]] = set()

    while queue:
        current_id, current_depth = queue.popleft()

        # Add current node
        if current_id in node_lookup:
            result_nodes[current_id] = node_lookup[current_id]

        # Stop if at max depth
        if current_depth >= depth:
            continue

        # Explore neighbors
        neighbors = adjacency.get(current_id, set())
        for neighbor_id in neighbors:
            # Add link (avoid duplicates)
            link_key = (min(current_id, neighbor_id), max(current_id, neighbor_id))
            if link_key not in seen_links:
                seen_links.add(link_key)
                # Find the original link
                if (current_id, neighbor_id) in link_lookup:
                    result_links.append(link_lookup[(current_id, neighbor_id)])
                elif (neighbor_id, current_id) in link_lookup:
                    result_links.append(link_lookup[(neighbor_id, current_id)])

            # Add to queue if not visited
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, current_depth + 1))

    return Graph(
        nodes=list(result_nodes.values()),
        links=result_links,
    )


def get_node_by_id(graph: Graph, node_id: str) -> Node | None:
    """Get a node by its ID.

    Args:
        graph: The knowledge graph.
        node_id: ID of the node to find.

    Returns:
        Node if found, None otherwise.
    """
    for node in graph.nodes:
        if node.id == node_id:
            return node
    return None


def get_links_for_node(graph: Graph, node_id: str) -> list[Link]:
    """Get all links connected to a node.

    Args:
        graph: The knowledge graph.
        node_id: ID of the node.

    Returns:
        List of links where node is source or target.
    """
    return [
        link for link in graph.links
        if link.source == node_id or link.target == node_id
    ]
