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
- **Obsidian Syntax Support** — Wikilinks, tags, embeds, frontmatter, nested tags, and canvas files

## Installation

Version **0.1.1** is free and MIT licensed. Requires Python 3.10+, access to a
local vault, and an agent able to run Python and read local files.

Download `unobsidian-0.1.1.zip` from [Releases](https://github.com/agent-hanju/unobsidian/releases/tag/0.1.1).
Extract its `unobsidian` folder into your project's `.claude/skills/` directory,
then install its dependencies using the Python interpreter your agent will run:

```bash
python -m pip install -r .claude/skills/unobsidian/requirements.txt
```

Alternatively, install the tagged source on macOS/Linux:

```bash
git clone --branch 0.1.1 https://github.com/agent-hanju/unobsidian.git
mkdir -p .claude/skills
cp -R unobsidian/skills/unobsidian .claude/skills/
python -m pip install -r .claude/skills/unobsidian/requirements.txt
```

On Windows PowerShell:

```powershell
git clone --branch 0.1.1 https://github.com/agent-hanju/unobsidian.git
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse unobsidian/skills/unobsidian .claude/skills/
python -m pip install -r .claude/skills/unobsidian/requirements.txt
```

Claude Code automatically picks up the skill and can query your vault's knowledge graph, traverse neighbors, search by tag, and resolve file paths — just point it at a vault directory.

Other agents need equivalent local skill/script access; compatibility with a
marketplace connector alone does not provide a Python runtime or vault access.

For writing documents in Obsidian syntax, use the [obsidian-markdown](https://github.com/kepano/obsidian-skills) skill alongside.

## Skills

The examples below run from the installed skill's `scripts` directory.
In `SKILL.md`, script paths use the local `${CLAUDE_SKILL_DIR}` directory.
Square-bracketed arguments in this README are optional syntax, not literal shell input.

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
Depth must be 1–3. Traversal is bidirectional, while returned links retain their
original direction and relationship type. To extract backlinks, select links
whose `target` equals the requested note ID.

### search_by_tag

Find all notes containing a specific tag, including nested tags.

```bash
python search_by_tag.py --vault /path/to/vault --tag project
```

Searching `#project` also matches `#project/frontend`, `#project/done`, etc.
Both `--tag project` and `--tag "#project"` are accepted.

### resolve_filepath

Resolve a note ID to its absolute path — disambiguates `.md` from `.canvas` files.
Use `ProjectA` for `ProjectA.md`, and `ProjectA.canvas` for a Canvas file.
Base file IDs likewise retain `.base`.

```bash
python resolve_filepath.py --vault /path/to/vault --file-id ProjectA
```

### visualize_graph

Render the full vault as an interactive D3.js force-directed graph and open it in a browser.

```bash
python visualize_graph.py --vault /path/to/vault [--output graph.html] [--no-open]
```

The default output is `<vault>/graph.html`. Use `--output` outside the vault to
avoid writing to the vault. Rendering requires network access to load D3.js from
d3js.org. The generated HTML includes filenames, tags, and relationships.

## Example requests

- "Find notes tagged `project`, read the relevant notes, and summarize the open tasks with source paths."
- "Explore two steps around `ProjectA`, read the connected notes, and explain their relationship."
- "Find notes linking to `ProjectA`; distinguish incoming links from outgoing links."

The scripts extract explicit graph relationships; they do not infer semantic
similarity. The agent must read the actual notes before making content claims.

## Output and limitations

- Graph and neighbor commands default to adjacency text; `--format d3` returns JSON.
- Tag search, file resolution, and visualization status return JSON. Runtime
  errors use JSON on stderr and a nonzero exit code; invalid CLI arguments use argparse errors.
- Node IDs omit `.md`, retain `.canvas`/`.base`, and must be unique across the
  vault. Same-name notes in different folders are not distinct graph nodes.
- Unresolved links may appear as graph nodes without a matching file.
- Queries reparse the vault on every invocation. There is no persistent index,
  live synchronization, or benchmarked large-vault performance guarantee.
- Query commands do not modify notes; visualization creates or replaces its output HTML.
- Vault contents read by your agent are handled by that agent and its AI provider.
  Treat generated graph HTML as private unless you intend to share its contents.

## Development

Install the skill requirements, then run the regression suite:

```bash
python -m unittest discover -s tests -v
```

See [CHANGELOG.md](CHANGELOG.md) for release changes.

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
