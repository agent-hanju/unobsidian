# MarkGraph

An MCP server that parses Obsidian-style markdown files and converts them into a knowledge graph.

[한국어](README-ko.md)

## Features

- **Lightweight**: Minimal dependencies (mcp, pydantic, python-frontmatter)
- **D3.js Compatible**: Output JSON can be used directly with `d3.forceSimulation()`
- **Neighbor Query**: BFS-based neighbor traversal with configurable depth
- **Obsidian Syntax Support**: Wikilinks, tags, embeds, frontmatter

## Installation

```bash
pip install markgraph
# or
uv add markgraph
```

## Usage

### Claude Desktop

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "markgraph": {
      "command": "uvx",
      "args": ["markgraph"]
    }
  }
}
```

### Claude Code CLI

```bash
claude mcp add markgraph -- uvx markgraph
```

### MCP Tools

#### `get_structure`

Parses markdown files and returns the full graph.

```json
{
  "paths": ["/path/to/vault"]
}
```

**Response:**
```json
{
  "nodes": [
    { "id": "NoteA", "type": "file", "label": "Note A", "metadata": {} }
  ],
  "links": [
    { "source": "NoteA", "target": "NoteB", "relation": "wikilink" }
  ]
}
```

#### `query_neighbors`

Parse markdown files and query neighbors of a specific node.

```json
{
  "paths": ["/path/to/vault"],
  "node_id": "MyNote",
  "depth": 2
}
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

## Visualization

Generate a D3.js-based HTML visualization using the `.claude/skills/markgraph-skill/scripts/visualize.py` script:

```bash
python visualize.py graph.json output.html
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
pytest tests/

# Test with MCP Inspector
npx @anthropic-ai/mcp-inspector markgraph
```

## License

MIT
