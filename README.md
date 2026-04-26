# Unobsidian

A Claude Code Skill that parses Obsidian-style markdown files and converts them into a knowledge graph.

## Features

- **Obsidian Independent**: Works without Obsidian installed or running
- **D3.js Compatible**: Use `--format d3` for JSON output compatible with `d3.forceSimulation()`
- **Neighbor Query**: BFS-based neighbor traversal with configurable depth
- **Obsidian Syntax Support**: Wikilinks, tags, embeds, frontmatter


## Installation

```bash
pip install obsidian-parse
git clone https://github.com/agent-hanju/unobsidian.git
cp -r unobsidian/skills/unobsidian/ .claude/skills/unobsidian/
```

Claude Code will automatically recognize the SKILL.md and perform knowledge graph queries, neighbor traversal, tag search, etc. with a vault path.

For writing documents in Obsidian syntax, use the [obsidian-markdown](https://github.com/kepano/obsidian-skills) skill alongside.

## Skills

### get_graph

Build a full knowledge graph from a vault.

```bash
python get_graph.py --vault /path/to/vault [--format adjacency|d3]
```

Default output is compressed adjacency format — one node per line, `#prefix` for tags, quoted names if spaces:
```
NoteA: NoteB #project
#project: NoteA "My Note"
```
Use `--format d3` for D3.js compatible JSON.

### get_neighbors

Query neighbors of a specific node via BFS traversal.

```bash
python get_neighbors.py --vault /path/to/vault --node MyNote --depth 2 [--format adjacency|d3]
```

Default output is compressed adjacency format. Use `--format d3` for D3.js compatible JSON.

### search_by_tag

Find documents containing a specific tag. (supports nested tags)

```bash
python search_by_tag.py --vault /path/to/vault --tag project
```

### resolve_filepath

Resolve a file ID to its absolute path within a vault.

```bash
python resolve_filepath.py --vault /path/to/vault --file-id ProjectA
```

### visualize_graph

Generate an interactive D3.js force-directed graph and open it in a browser.

```bash
python visualize_graph.py --vault /path/to/vault [--output graph.html] [--no-open]
```

## Data Model

### Node

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Filename or #tag name |
| `type` | "file" \| "tag" | Node type |
| `label` | string? | Display label |
| `metadata` | object | Frontmatter data |

### Link

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Source node ID |
| `target` | string | Target node ID |
| `relation` | "wikilink" \| "embed" \| "tag" | Relation type |
| `metadata` | object | Additional metadata |

## Parsing Rules

| Pattern | Relation |
|---------|----------|
| `[[Target]]` | wikilink |
| `[[Target\|Alias]]` | wikilink |
| `![[Embed]]` | embed |
| `#Tag` | tag |

**Excluded from parsing:**

- Code fences (` ``` `)
- Inline code (`` ` ``)
- YAML frontmatter (extracted separately)

## License

MIT
