# Unobsidian

**A Claude Code Skill for exploring Obsidian vaults as a knowledge graph — no Obsidian required.**

[![PyPI](https://img.shields.io/pypi/v/obsidian-parse?label=obsidian-parse)](https://pypi.org/project/obsidian-parse/)
[![Python](https://img.shields.io/pypi/pyversions/obsidian-parse)](https://pypi.org/project/obsidian-parse/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **Obsidian Independent** — Parses vaults directly from the filesystem, no Obsidian installation needed
- **LLM-friendly output** — Compressed adjacency format keeps token usage low while staying human-readable
- **D3.js Compatible** — Use `--format d3` for JSON output ready for `d3.forceSimulation()`
- **BFS Neighbor Traversal** — Explore note connections up to configurable depth
- **Full Obsidian Syntax** — Wikilinks, tags, embeds, frontmatter, nested tags, canvas files

## Installation

```bash
pip install obsidian-parse
git clone https://github.com/agent-hanju/unobsidian.git
cp -r unobsidian/skills/unobsidian/ .claude/skills/unobsidian/
```

Claude Code automatically picks up the skill and can query your vault's knowledge graph, traverse neighbors, search by tag, and resolve file paths — just point it at a vault directory.

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

Explore the local neighborhood of any note or tag via BFS traversal.

```bash
python get_neighbors.py --vault /path/to/vault --node MyNote --depth 2 [--format adjacency|d3]
```

Default output is compressed adjacency format. Use `--format d3` for D3.js compatible JSON.

### search_by_tag

Find all notes containing a specific tag, including nested tags.

```bash
python search_by_tag.py --vault /path/to/vault --tag project
```

Searching `#project` also matches `#project/frontend`, `#project/done`, etc.

### resolve_filepath

Resolve a note ID to its absolute path — disambiguates `.md` from `.canvas` files.

```bash
python resolve_filepath.py --vault /path/to/vault --file-id ProjectA
```

### visualize_graph

Render the full vault as an interactive D3.js force-directed graph and open it in a browser.

```bash
python visualize_graph.py --vault /path/to/vault [--output graph.html] [--no-open]
```

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
