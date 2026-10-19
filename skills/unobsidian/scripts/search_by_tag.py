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
    """샵 접두사가 선택적인 태그로 해당 태그와 하위 태그의 노트를 조회한다."""
    parser = argparse.ArgumentParser(description="Search vault documents by tag")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--tag", required=True, help="Tag to search for (optional # prefix)")
    args = parser.parse_args()

    try:
        tag = args.tag.removeprefix("#")
        if not tag:
            raise ValueError("Tag must not be empty")
        raw = parse([args.vault])
        results = []
        for result in raw:
            for name in result.tag_names:
                if tag in expand_nested_tag(name):
                    results.append({"file_id": result.file_id, "tags": result.tag_names})
                    break
        print(json.dumps({"results": results, "count": len(results)}, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
