#!/usr/bin/env python3
"""보관함의 연결 그래프를 인접 목록 텍스트 또는 D3 JSON으로 출력한다.

기본 출력은 한 줄에 한 노드를 표시하며 태그 ID에는 # 접두사가 있다.
--format d3의 노드는 id와 type, 링크는 source·target·relation을 포함한다.
.obsidian/app.json의 제외 규칙은 파서에서 적용한다.
"""

import argparse
import json
import sys

from obsidian_parse.parser.engine import parse
from obsidian_parse.utils.graph import results_to_d3


def _q(node_id: str) -> str:
    return f'"{node_id}"' if " " in node_id else node_id


def to_adjacency(graph: dict) -> str:
    adj: dict[str, list[str]] = {n["id"]: [] for n in graph["nodes"]}
    for link in graph["links"]:
        adj[link["source"]].append(link["target"])
    lines = [
        f"{_q(node)}: {' '.join(_q(n) for n in neighbors)}" if neighbors else _q(node)
        for node, neighbors in sorted(adj.items())
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build knowledge graph from vault")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--format", choices=["adjacency", "d3"], default="adjacency",
                        help="Output format (default: adjacency)")
    args = parser.parse_args()

    try:
        graph = results_to_d3(parse([args.vault]))

        if args.format == "d3":
            for node in graph["nodes"]:
                node.pop("label", None)
            print(json.dumps(graph, ensure_ascii=False, indent=2))
        else:
            print(to_adjacency(graph))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
