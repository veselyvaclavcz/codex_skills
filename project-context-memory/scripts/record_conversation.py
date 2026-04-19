#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "conversation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a project conversation note.")
    parser.add_argument("--root", required=True, help="Project root directory.")
    parser.add_argument("--title", required=True, help="Conversation title.")
    parser.add_argument("--summary", help="Inline summary text.")
    parser.add_argument("--summary-file", help="Path to a UTF-8 summary file.")
    parser.add_argument("--status", default="completed", help="Conversation status.")
    parser.add_argument("--tag", action="append", default=[], help="Repeatable tag.")
    parser.add_argument("--file", action="append", default=[], help="Repeatable impacted file path.")
    parser.add_argument("--decision", action="append", default=[], help="Repeatable durable decision.")
    parser.add_argument("--question", action="append", default=[], help="Repeatable open question.")
    parser.add_argument("--next-step", action="append", default=[], help="Repeatable next step.")
    parser.add_argument("--timestamp", help="Override timestamp in YYYY-MM-DDTHH:MM format.")
    return parser.parse_args()


def read_summary(args: argparse.Namespace) -> str:
    if args.summary:
        return args.summary.strip()
    if args.summary_file:
        return Path(args.summary_file).read_text(encoding="utf-8").strip()
    raise SystemExit("Provide --summary or --summary-file.")


def format_list(items: list[str], empty_line: str) -> str:
    if not items:
        return f"- {empty_line}"
    return "\n".join(f"- {item}" for item in items)


def build_note(args: argparse.Namespace, timestamp: datetime, summary: str) -> str:
    tags = ", ".join(args.tag) if args.tag else ""
    return (
        "---\n"
        f"title: {args.title}\n"
        f"created_at: {timestamp.isoformat(timespec='minutes')}\n"
        f"status: {args.status}\n"
        f"tags: {tags}\n"
        "---\n\n"
        "# Summary\n\n"
        f"{summary}\n\n"
        "# Decisions\n\n"
        f"{format_list(args.decision, 'No durable decisions captured yet.')}\n\n"
        "# Open Questions\n\n"
        f"{format_list(args.question, 'No open questions captured yet.')}\n\n"
        "# Impacted Files\n\n"
        f"{format_list(args.file, 'No specific files recorded.')}\n\n"
        "# Next Steps\n\n"
        f"{format_list(args.next_step, 'No explicit next steps recorded.')}\n"
    )


def rebuild_index(conversations_root: Path) -> None:
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
            title_match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
            created_match = re.search(r"^created_at:\s*(.+)$", text, re.MULTILINE)
            status_match = re.search(r"^status:\s*(.+)$", text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else note.stem
            created = created_match.group(1).strip() if created_match else "unknown"
            status = status_match.group(1).strip() if status_match else "unknown"
            relative = note.relative_to(conversations_root.parent).as_posix()
            lines.append(f"- `{created}` [{title}]({relative}) - `{status}`")
    (conversations_root / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    memory_root = root / "docs" / "project-memory"
    conversations_root = memory_root / "conversations"
    if not memory_root.exists():
        raise SystemExit(
            f"Project memory is missing at {memory_root}. Bootstrap first with bootstrap_project_memory.py."
        )

    timestamp = (
        datetime.strptime(args.timestamp, "%Y-%m-%dT%H:%M")
        if args.timestamp
        else datetime.now()
    )
    summary = read_summary(args)
    slug = slugify(args.title)
    year_dir = conversations_root / f"{timestamp.year:04d}"
    year_dir.mkdir(parents=True, exist_ok=True)
    note_path = year_dir / f"{timestamp.strftime('%Y-%m-%d-%H%M')}-{slug}.md"
    note_path.write_text(build_note(args, timestamp, summary), encoding="utf-8")
    rebuild_index(conversations_root)
    print(note_path)


if __name__ == "__main__":
    main()
