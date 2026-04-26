#!/usr/bin/env python3
"""Get BFS neighbor subgraph for a node in the vault.

Usage:
    python get_neighbors.py --vault /path/to/vault --node NoteTitle [--depth 2] [--format adjacency|d3]

--node: file ID (filename without .md) or tag with # prefix (e.g. #project)
--depth: BFS traversal depth, 1–3 (default: 1)

Default output (adjacency):
    { "files": {"NoteA": ["NoteB", ...]}, "tags": {"#tag": [...]} }

D3 output (--format d3):
    { "nodes": [{"id", "type"}], "links": [{"source", "target", "relation"}] }
"""

import argparse
import json
import sys
from collections import deque

from obsidian_parse.parser.engine import parse
from obsidian_parse.utils.errors import NodeNotFoundError
from obsidian_parse.utils.graph import results_to_d3


def _q(node_id: str) -> str:
    return f'"{node_id}"' if " " in node_id else node_id


def to_adjacency(nodes: dict, links: list) -> str:
    adj: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for link in links:
        adj[link["source"]].append(link["target"])
    lines = [
        f"{_q(node)}: {' '.join(_q(n) for n in neighbors)}" if neighbors else _q(node)
        for node, neighbors in sorted(adj.items())
    ]
    return "\n".join(lines)


def build_undirected(links: list) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {}
    for lnk in links:
        adj.setdefault(lnk["source"], set()).add(lnk["target"])
        adj.setdefault(lnk["target"], set()).add(lnk["source"])
    return adj


def bfs(start: str, depth: int, adj: dict, links: list) -> tuple[set[str], list]:
    visited: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    node_ids: set[str] = {start}
    result_links: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str]] = set()

    while queue:
        current, d = queue.popleft()
        if d >= depth:
            continue
        for neighbor in adj.get(current, set()):
            key = (min(current, neighbor), max(current, neighbor))
            if key not in seen_keys:
                seen_keys.add(key)
                pair = {current, neighbor}
                found = next((lnk for lnk in links if {lnk["source"], lnk["target"]} == pair), None)
                if found:
                    result_links.append(found)
            node_ids.add(neighbor)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, d + 1))

    return node_ids, result_links


def main() -> None:
    parser = argparse.ArgumentParser(description="BFS neighbor subgraph for a node")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--node", required=True, help="Node ID (filename without .md, or #tag)")
    parser.add_argument("--depth", type=int, default=1, help="BFS depth, 1–3 (default: 1)")
    parser.add_argument("--format", choices=["adjacency", "d3"], default="adjacency",
                        help="Output format (default: adjacency)")
    args = parser.parse_args()

    try:
        depth = max(1, min(3, args.depth))
        graph = results_to_d3(parse([args.vault]))
        nodes = {n["id"]: n for n in graph["nodes"]}
        type_map = {n["id"]: n["type"] for n in graph["nodes"]}

        if args.node not in nodes:
            raise NodeNotFoundError(args.node)

        node_ids, result_links = bfs(args.node, depth, build_undirected(graph["links"]), graph["links"])
        result_nodes = {i: nodes[i] for i in node_ids if i in nodes}

        if args.format == "d3":
            for node in result_nodes.values():
                node.pop("label", None)
            print(json.dumps({"nodes": list(result_nodes.values()), "links": result_links},
                             ensure_ascii=False, indent=2))
        else:
            print(to_adjacency(result_nodes, result_links))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
