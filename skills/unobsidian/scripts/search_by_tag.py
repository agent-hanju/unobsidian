#!/usr/bin/env python3
"""Search vault documents by tag.

Usage:
    python search_by_tag.py --vault /path/to/vault --tag project

Nested tag matching is supported: searching for "project" also matches
documents tagged with #project/frontend, #project/backend, etc.

Outputs JSON: { "results": [{ "file_id", "tags" }], "count": N }
"""

import argparse
import json
import sys

from obsidian_parse.parser.engine import parse
from obsidian_parse.utils.tags import expand_nested_tag


def main() -> None:
    parser = argparse.ArgumentParser(description="Search vault documents by tag")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--tag", required=True, help="Tag to search for (without # prefix)")
    args = parser.parse_args()

    try:
        raw = parse([args.vault])
        results = [
            {"file_id": r.file_id, "tags": r.tag_names}
            for r in raw
            if args.tag in {t for name in r.tag_names for t in expand_nested_tag(name)}
        ]
        print(json.dumps({"results": results, "count": len(results)}, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
