#!/usr/bin/env python3
"""List stale translated Markdown files for docs -> docs_ua."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List stale or missing Ukrainian translations by comparing modification "
            "times between docs/ and docs_ua/."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing docs/ and docs_ua/ (default: current directory).",
    )
    return parser


def iter_source_files(source_root: Path) -> list[Path]:
    return sorted(path for path in source_root.rglob("*.md") if path.is_file())


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    source_root = repo_root / "docs"
    target_root = repo_root / "docs_ua"

    if not source_root.is_dir():
        parser.error(f"missing source directory: {source_root}")

    stale_entries: list[dict[str, str]] = []

    for source_path in iter_source_files(source_root):
        relative_path = source_path.relative_to(source_root)
        target_path = target_root / relative_path

        if not target_path.exists():
            stale_entries.append(
                {
                    "source": source_path.relative_to(repo_root).as_posix(),
                    "target": target_path.relative_to(repo_root).as_posix(),
                    "reason": "missing_translation",
                }
            )
            continue

        if source_path.stat().st_mtime_ns > target_path.stat().st_mtime_ns:
            stale_entries.append(
                {
                    "source": source_path.relative_to(repo_root).as_posix(),
                    "target": target_path.relative_to(repo_root).as_posix(),
                    "reason": "source_newer",
                }
            )

    json.dump(stale_entries, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
