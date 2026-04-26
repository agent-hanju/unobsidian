#!/usr/bin/env python3
"""Generate an interactive D3.js knowledge graph visualization and open it in a browser.

Usage:
    python visualize_graph.py --vault /path/to/vault [--output graph.html] [--no-open]

Outputs an HTML file with a force-directed graph. Nodes are sized and colored by
connection count. Click a node to highlight its neighbors; click empty space to reset.
"""

import argparse
import json
import subprocess
import sys
import webbrowser
from pathlib import Path

from obsidian_parse.parser.engine import parse
from obsidian_parse.utils.graph import results_to_d3


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title} — Knowledge Graph</title>
<style>
  body {{ margin: 0; background: #0f0f1a; font-family: sans-serif; overflow: hidden; }}
  .node circle {{ cursor: pointer; stroke-width: 1.5; }}
  .node text {{ font-size: 11px; fill: #ccc; pointer-events: none; }}
  .link {{ stroke: #334; stroke-opacity: 0.6; }}
  #info {{
    position: fixed; top: 16px; right: 16px;
    background: #1a1a2e; color: #aaa;
    padding: 12px 16px; border-radius: 8px;
    font-size: 13px; max-width: 260px; border: 1px solid #334;
  }}
  #info h3 {{ margin: 0 0 6px; color: #e0e0ff; font-size: 15px; }}
  #tooltip {{
    position: fixed; background: #1a1a2e; color: #ccc;
    padding: 8px 12px; border-radius: 6px; font-size: 12px;
    pointer-events: none; display: none; border: 1px solid #556;
  }}
  #controls {{ position: fixed; bottom: 16px; left: 16px; color: #555; font-size: 11px; }}
</style>
</head>
<body>
<svg id="graph"></svg>
<div id="info">
  <h3>{title}</h3>
  <div>노드: <b style="color:#8af">{node_count}</b> &nbsp; 링크: <b style="color:#8af">{link_count}</b></div>
  <div style="margin-top:8px;font-size:11px;color:#778">
    노드 클릭 시 이웃 하이라이트<br>드래그로 이동 / 스크롤로 줌<br>빈 곳 클릭으로 초기화
  </div>
</div>
<div id="tooltip"></div>
<div id="controls">scroll to zoom · drag to pan</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const graph = {graph_data};

const width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#graph").attr("width", width).attr("height", height);
const g = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 4]).on("zoom", e => g.attr("transform", e.transform)));

const degree = {{}};
graph.links.forEach(l => {{
  degree[l.source] = (degree[l.source] || 0) + 1;
  degree[l.target] = (degree[l.target] || 0) + 1;
}});

const maxDeg = Object.values(degree).length > 0 ? Math.max(...Object.values(degree)) : 1;
const rScale = d => 4 + (degree[d.id] || 0) / maxDeg * 20;
const colorScale = d3.scaleSequential(d3.interpolatePlasma).domain([0, maxDeg]);

const sim = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id).distance(70))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(d => rScale(d) + 5));

const link = g.append("g").selectAll("line")
  .data(graph.links).join("line").attr("class", "link").attr("stroke-width", 1);

const node = g.append("g").selectAll(".node")
  .data(graph.nodes).join("g").attr("class", "node")
  .call(d3.drag()
    .on("start", (e, d) => {{ if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
    .on("drag",  (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on("end",   (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }}));

node.append("circle")
  .attr("r", rScale)
  .attr("fill", d => colorScale(degree[d.id] || 0))
  .attr("stroke", "#0f0f1a");

node.append("text")
  .attr("dx", d => rScale(d) + 3)
  .attr("dy", "0.35em")
  .text(d => d.label.replace(/_/g, " "));

const tooltip = document.getElementById("tooltip");

node.on("mouseover", (e, d) => {{
  tooltip.style.display = "block";
  const bold = document.createElement("b");
  bold.textContent = d.label.replace(/_/g, " ");
  tooltip.textContent = "";
  tooltip.appendChild(bold);
  tooltip.appendChild(document.createElement("br"));
  tooltip.appendChild(document.createTextNode((d.type === "tag" ? "태그" : "파일") + " · 연결: " + (degree[d.id] || 0)));
}}).on("mousemove", e => {{
  tooltip.style.left = (e.clientX + 14) + "px";
  tooltip.style.top  = (e.clientY - 10) + "px";
}}).on("mouseout", () => {{ tooltip.style.display = "none"; }});

node.on("click", (e, d) => {{
  e.stopPropagation();
  const neighbors = new Set([d.id]);
  graph.links.forEach(l => {{
    const s = typeof l.source === "object" ? l.source.id : l.source;
    const t = typeof l.target === "object" ? l.target.id : l.target;
    if (s === d.id) neighbors.add(t);
    if (t === d.id) neighbors.add(s);
  }});
  node.selectAll("circle").attr("opacity", n => neighbors.has(n.id) ? 1 : 0.12);
  node.selectAll("text").attr("opacity",   n => neighbors.has(n.id) ? 1 : 0.08);
  link.attr("stroke-opacity", l => {{
    const s = typeof l.source === "object" ? l.source.id : l.source;
    const t = typeof l.target === "object" ? l.target.id : l.target;
    return (s === d.id || t === d.id) ? 0.9 : 0.04;
  }});
}});

svg.on("click", () => {{
  node.selectAll("circle").attr("opacity", 1);
  node.selectAll("text").attr("opacity", 1);
  link.attr("stroke-opacity", 0.6);
}});

sim.on("tick", () => {{
  link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
}});
</script>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize vault knowledge graph")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--output", default=None, help="Output HTML file path (default: <vault>/graph.html)")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    vault_root = Path(args.vault)
    output_path = Path(args.output) if args.output else vault_root / "graph.html"

    try:
        if not vault_root.exists():
            raise FileNotFoundError(f"Vault path does not exist: {vault_root}")
        if not vault_root.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {vault_root}")

        graph = results_to_d3(parse([str(vault_root)]))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        title = vault_root.name
        graph_data = json.dumps(graph, ensure_ascii=False)
        html = HTML_TEMPLATE.format(
            title=title,
            node_count=len(graph["nodes"]),
            link_count=len(graph["links"]),
            graph_data=graph_data,
        )

        output_path.write_text(html, encoding="utf-8")
        print(json.dumps({"output": str(output_path)}, ensure_ascii=False))

        if not args.no_open:
            webbrowser.open(output_path.as_uri())

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
