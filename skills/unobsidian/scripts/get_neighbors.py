#!/usr/bin/env python3
"""양방향 BFS로 지정한 반경의 노드와 그 사이의 모든 원본 링크를 조회한다.

기본 출력은 한 줄에 한 노드를 표시하는 인접 목록 텍스트다.
--format d3를 지정하면 nodes와 links를 포함한 JSON을 출력한다.
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
    """최단 거리가 depth 이하인 노드와 해당 노드 사이의 원본 링크를 반환한다.

    adj는 links에서 만든 무방향 인접 목록이어야 한다. BFS는 거리 순서로
    노드를 방문하므로 depth에서 확장을 중단해도 반경 내 모든 노드를 찾는다.
    링크를 별도로 순회해 방향과 관계 종류 및 원본 순서를 보존한다.
    시간 복잡도와 추가 공간은 O(V + E) 이하다.
    """
    visited: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])

    while queue:
        entry = queue.popleft()
        current = entry[0]
        d = entry[1]
        if d >= depth:
            continue
        for neighbor in adj.get(current, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, d + 1))

    result_links = []
    for link in links:
        if link["source"] in visited and link["target"] in visited:
            result_links.append(link)
    return visited, result_links


def main() -> None:
    """보관함을 조회하고 선택한 형식의 이웃 그래프를 출력한다."""
    parser = argparse.ArgumentParser(description="BFS neighbor subgraph for a node")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--node", required=True, help="Node ID (filename without .md, or #tag)")
    parser.add_argument("--depth", type=int, choices=range(1, 4), default=1,
                        help="BFS depth, 1–3 (default: 1)")
    parser.add_argument("--format", choices=["adjacency", "d3"], default="adjacency",
                        help="Output format (default: adjacency)")
    args = parser.parse_args()

    try:
        graph = results_to_d3(parse([args.vault]))
        nodes = {n["id"]: n for n in graph["nodes"]}

        if args.node not in nodes:
            raise NodeNotFoundError(args.node)

        node_ids, result_links = bfs(args.node, args.depth, build_undirected(graph["links"]), graph["links"])
        result_nodes = {}
        for node in graph["nodes"]:
            if node["id"] in node_ids:
                result_nodes[node["id"]] = node

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
