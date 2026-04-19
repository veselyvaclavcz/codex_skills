#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
CREATED_RE = re.compile(r"^created_at:\s*(.+)$", re.MULTILINE)
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild project conversation index.")
    parser.add_argument("--root", required=True, help="Project root directory.")
    return parser.parse_args()


def extract(pattern: re.Pattern[str], text: str, fallback: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else fallback


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    conversations_root = root / "docs" / "project-memory" / "conversations"
    if not conversations_root.exists():
        raise SystemExit(f"Conversation root does not exist: {conversations_root}")

    notes = sorted(
        [
            path
            for path in conversations_root.rglob("*.md")
            if path.name.lower() != "index.md"
        ],
        reverse=True,
    )

    lines = [
        "# Conversation Index",
        "",
        "Most recent notes first.",
        "",
    ]
    if not notes:
        lines.append("- No conversation notes yet.")
    else:
        for note in notes:
            text = note.read_text(encoding="utf-8")
            title = extract(TITLE_RE, text, note.stem)
            created = extract(CREATED_RE, text, "unknown")
            status = extract(STATUS_RE, text, "unknown")
            relative = note.relative_to(conversations_root.parent).as_posix()
            lines.append(f"- `{created}` [{title}]({relative}) - `{status}`")

    index_path = conversations_root / "index.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(index_path)


if __name__ == "__main__":
    main()
