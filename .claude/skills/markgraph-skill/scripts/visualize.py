#!/usr/bin/env python3
"""Generate D3.js HTML visualization from graph JSON."""

import json
import sys
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarkGraph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            overflow: hidden;
        }
        svg {
            display: block;
        }
        .node {
            cursor: pointer;
        }
        .node circle {
            stroke: #fff;
            stroke-width: 2px;
        }
        .node.file circle {
            fill: #4ecdc4;
        }
        .node.tag circle {
            fill: #ff6b6b;
        }
        .node text {
            fill: #fff;
            font-size: 12px;
            pointer-events: none;
        }
        .link {
            stroke-opacity: 0.6;
        }
        .link.wikilink {
            stroke: #4ecdc4;
        }
        .link.embed {
            stroke: #ffe66d;
            stroke-dasharray: 5,5;
        }
        .link.tag {
            stroke: #ff6b6b;
            stroke-dasharray: 2,2;
        }
        .tooltip {
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
        }
        .legend {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 8px;
            color: #fff;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 20px;
            height: 3px;
            margin-right: 10px;
        }
        .legend-circle {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div><strong>Nodes</strong></div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #4ecdc4;"></div>
            <span>File</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #ff6b6b;"></div>
            <span>Tag</span>
        </div>
        <div style="margin-top: 10px;"><strong>Links</strong></div>
        <div class="legend-item">
            <div class="legend-color" style="background: #4ecdc4;"></div>
            <span>Wikilink</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ffe66d; border-style: dashed;"></div>
            <span>Embed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff6b6b; border-style: dotted;"></div>
            <span>Tag</span>
        </div>
    </div>
    <div class="tooltip"></div>
    <svg></svg>
    <script>
        const data = __GRAPH_DATA__;

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("svg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g");

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform));

        svg.call(zoom);

        // Force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));

        // Links
        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", d => `link ${d.relation}`)
            .attr("stroke-width", 2);

        // Nodes
        const node = g.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", d => `node ${d.type}`)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", d => d.type === "tag" ? 8 : 12);

        node.append("text")
            .text(d => d.label || d.id)
            .attr("dx", 15)
            .attr("dy", 4);

        // Tooltip
        const tooltip = d3.select(".tooltip");

        node.on("mouseover", (event, d) => {
            tooltip
                .style("opacity", 1)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .html(`<strong>${d.id}</strong><br>Type: ${d.type}`);
        })
        .on("mouseout", () => tooltip.style("opacity", 0));

        // Simulation tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });

        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        // Resize handler
        window.addEventListener("resize", () => {
            const w = window.innerWidth;
            const h = window.innerHeight;
            svg.attr("width", w).attr("height", h);
            simulation.force("center", d3.forceCenter(w / 2, h / 2));
            simulation.alpha(0.3).restart();
        });
    </script>
</body>
</html>
"""


def generate_html(graph_data: dict) -> str:
    """Generate HTML visualization from graph data.

    Args:
        graph_data: Graph dictionary with 'nodes' and 'links' arrays.

    Returns:
        Complete HTML string with embedded D3.js visualization.
    """
    json_str = json.dumps(graph_data, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__GRAPH_DATA__", json_str)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: visualize.py <input.json> <output.html>")
        print("       visualize.py - <output.html>  (read from stdin)")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Read input
    if input_path == "-":
        graph_data = json.load(sys.stdin)
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

    # Generate HTML
    html = generate_html(graph_data)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
