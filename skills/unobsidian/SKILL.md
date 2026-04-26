---
name: unobsidian
description: Parse an Obsidian vault and explore its knowledge graph. Use when you need to query note connections, traverse neighbors of a node, search by tag, or resolve file paths within a vault.
allowed-tools: Bash(python *) Bash(uv *) Bash(pip *)
---

# Unobsidian

A skill for parsing Obsidian-style markdown files and exploring the knowledge graph.
Works without Obsidian installed or running.

## Prerequisites

```bash
pip install obsidian-parse
```

## Commands

All commands take `--vault` as the path to the vault directory.
Output is always JSON.

### Full graph

```bash
python ${CLAUDE_SKILL_DIR}/scripts/get_graph.py --vault /path/to/vault [--format adjacency|d3]
```

Parses all markdown files and builds a knowledge graph.
Default output is compressed adjacency format (one node per line, `#prefix` for tags, quoted if name contains spaces). Use `--format d3` for D3.js compatible JSON.

### Neighbor traversal

```bash
python ${CLAUDE_SKILL_DIR}/scripts/get_neighbors.py --vault /path/to/vault --node MyNote --depth 2 [--format adjacency|d3]
```

- `--node`: Node ID (filename without `.md`, or `#tagname` for tags)
- `--depth`: BFS depth (default: 1, max: 3)
- `--format`: Output format (default: adjacency — compressed text, d3 also supported)

### Tag search

```bash
python ${CLAUDE_SKILL_DIR}/scripts/search_by_tag.py --vault /path/to/vault --tag project
```

Supports nested tags. Searching `#project` also matches `#project/frontend`.

### Resolve file path

```bash
python ${CLAUDE_SKILL_DIR}/scripts/resolve_filepath.py --vault /path/to/vault --file-id ProjectA
```

### Visualize graph

```bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize_graph.py --vault /path/to/vault [--output graph.html] [--no-open]
```

Renders the full vault graph as an interactive D3.js force-directed HTML file and opens it in a browser.
`--output` sets the output path (default: `<vault>/graph.html`), `--no-open` disables auto-open.

## Key notes

- Output is always JSON
- Node types: `file` (markdown file), `tag`
- Link types: `wikilink`, `embed`, `tag`
- Node ID is the filename without `.md` — must be unique within the vault
- Backlinks (notes pointing to a given note): use get_neighbors — it traverses bidirectionally
