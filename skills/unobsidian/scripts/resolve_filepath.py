#!/usr/bin/env python3
"""Resolve a file ID to its absolute path within a vault.

Usage:
    python resolve_filepath.py --vault /path/to/vault --file-id ProjectA

Outputs JSON: { "path": "/absolute/path/to/ProjectA.md" }
"""

import argparse
import json
import sys
from pathlib import Path

from obsidian_parse.utils.vault import find_file_by_id


def main() -> None:
    """파일 ID를 조회하고 보관함 내 파일의 절대경로를 JSON으로 출력한다."""
    parser = argparse.ArgumentParser(description="Resolve file ID to path")
    parser.add_argument("--vault", required=True, help="Path to vault directory")
    parser.add_argument("--file-id", required=True, help="Filename without .md extension")
    args = parser.parse_args()

    try:
        vault_root = Path(args.vault).resolve()
        rel = find_file_by_id(vault_root, args.file_id)
        if rel is None:
            print(json.dumps({"error": f"File '{args.file_id}' not found"}), file=sys.stderr)
            sys.exit(1)
        print(json.dumps({"path": str(vault_root / rel)}, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
