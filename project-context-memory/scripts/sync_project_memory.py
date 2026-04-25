#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from record_conversation import build_note, read_summary, rebuild_index, slugify


PROJECT_MARKERS = [
    ".git",
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "*.sln",
]
AGENTS_BEGIN = "<!-- PROJECT-CONTEXT-MEMORY:BEGIN -->"
AGENTS_END = "<!-- PROJECT-CONTEXT-MEMORY:END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auto-bootstrap and maintain shared project memory."
    )
    parser.add_argument(
        "--mode",
        choices=["start", "checkpoint", "finish"],
        required=True,
        help="start bootstraps and reports memory paths; checkpoint and finish also write a conversation note.",
    )
    parser.add_argument("--root", help="Optional project root. Defaults to autodetect from cwd.")
    parser.add_argument("--cwd", help="Optional working directory for autodetection.")
    parser.add_argument("--project-name", help="Optional project name override during bootstrap.")
    parser.add_argument("--title", help="Conversation title for checkpoint or finish.")
    parser.add_argument("--summary", help="Inline summary text for checkpoint or finish.")
    parser.add_argument("--summary-file", help="Path to a summary file for checkpoint or finish.")
    parser.add_argument("--status", help="Explicit note status override.")
    parser.add_argument("--tag", action="append", default=[], help="Repeatable tag.")
    parser.add_argument("--file", action="append", default=[], help="Repeatable impacted file.")
    parser.add_argument("--decision", action="append", default=[], help="Repeatable durable decision.")
    parser.add_argument("--question", action="append", default=[], help="Repeatable open question.")
    parser.add_argument("--next-step", action="append", default=[], help="Repeatable next step.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    return parser.parse_args()


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    candidates = [current, *current.parents]
    for path in candidates:
        for marker in PROJECT_MARKERS:
            if "*" in marker:
                if list(path.glob(marker)):
                    return path
            elif (path / marker).exists():
                return path
    return current


def ensure_bootstrap(root: Path, project_name: str | None) -> Path:
    memory_root = root / "docs" / "project-memory"
    if memory_root.exists():
        return memory_root

    template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    replacements = {
        "PROJECT_NAME": project_name or root.name,
        "PROJECT_ROOT": str(root),
        "MEMORY_ROOT": str(memory_root),
    }
    files = {
        memory_root / "README.md": render_template(template_dir / "README.md.tmpl", replacements),
        memory_root / "project-summary.md": render_template(template_dir / "project-summary.md.tmpl", replacements),
        memory_root / "current-state.md": render_template(template_dir / "current-state.md.tmpl", replacements),
        memory_root / "decisions.md": render_template(template_dir / "decisions.md.tmpl", replacements),
        memory_root / "open-questions.md": render_template(template_dir / "open-questions.md.tmpl", replacements),
        memory_root / "conventions.md": render_template(template_dir / "conventions.md.tmpl", replacements),
        memory_root / "conversations" / "index.md": render_template(template_dir / "conversations-index.md.tmpl", replacements),
    }
    year_dir = memory_root / "conversations" / f"{datetime.now().year:04d}"
    year_dir.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    memory_json = memory_root / "memory.json"
    if not memory_json.exists():
        memory_json.write_text(
            json.dumps(
                {
                    "project_name": project_name or root.name,
                    "project_root": str(root),
                    "memory_root": str(memory_root),
                    "schema_version": 1,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return memory_root


def build_agents_block(root: Path) -> str:
    return (
        f"{AGENTS_BEGIN}\n"
        "# Codex Project Operating Rules\n\n"
        "Use shared project memory by default for substantial work in this repository.\n\n"
        "## Required Memory Workflow\n\n"
        "1. At thread start, run:\n"
        f"   `python \"C:\\Users\\mail\\.codex\\skills\\project-context-memory\\scripts\\sync_project_memory.py\" --mode start --root \"{root}\"`\n"
        "2. Read the files reported by the sync script before making a plan.\n"
        "3. Record meaningful checkpoints and thread endings with the same sync script using `--mode checkpoint` or `--mode finish`.\n\n"
        "## Cost-Aware Workflow Rules\n\n"
        "Use `$codex-cost-aware-workflow` when RTK or Codex subagent delegation is actually worth it.\n\n"
        "Prefer this split:\n"
        "- Keep final planning, risky decisions, and user-facing synthesis in Codex.\n"
        "- Use custom subagents for bounded exploration, small changes, review, and summaries when that saves time or tokens.\n"
        "- Do not delegate trivial work or tasks whose value is mostly in integration.\n\n"
        "Default subagents:\n"
        "- `explorer-fast`: read-only reconnaissance\n"
        "- `worker-cheap`: small localized changes\n"
        "- `reviewer-mini`: focused review\n"
        "- `summarizer-nano`: logs, docs, extraction, and summaries\n\n"
        "Token discipline:\n"
        "- Do not forward the whole conversation by default.\n"
        "- Send only the minimal context, artifacts, and acceptance criteria needed for the delegated subtask.\n"
        "- Treat subagent output as advisory; Codex keeps final edits and review.\n"
        f"{AGENTS_END}\n"
    )


def ensure_agents_file(root: Path) -> Path:
    agents_path = root / "AGENTS.md"
    managed_block = build_agents_block(root)
    if not agents_path.exists():
        agents_path.write_text(
            "# AGENTS\n\n"
            "This file contains repository-specific operating rules for Codex and related agents.\n\n"
            + managed_block,
            encoding="utf-8",
        )
        return agents_path

    existing = agents_path.read_text(encoding="utf-8")
    if AGENTS_BEGIN in existing and AGENTS_END in existing:
        updated = re.sub(
            rf"{re.escape(AGENTS_BEGIN)}.*?{re.escape(AGENTS_END)}\n?",
            managed_block,
            existing,
            flags=re.DOTALL,
        )
        if updated != existing:
            agents_path.write_text(updated, encoding="utf-8")
        return agents_path

    agents_path.write_text(existing.rstrip() + "\n\n" + managed_block, encoding="utf-8")
    return agents_path


def render_template(path: Path, replacements: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def record_note(args: argparse.Namespace, root: Path, memory_root: Path) -> Path:
    if not args.title:
        raise SystemExit("--title is required for checkpoint and finish modes.")
    if not args.summary and not args.summary_file:
        raise SystemExit("--summary or --summary-file is required for checkpoint and finish modes.")

    timestamp = datetime.now()
    conversations_root = memory_root / "conversations"
    year_dir = conversations_root / f"{timestamp.year:04d}"
    year_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.title)
    note_path = year_dir / f"{timestamp.strftime('%Y-%m-%d-%H%M')}-{slug}.md"

    status = args.status or ("in-progress" if args.mode == "checkpoint" else "completed")
    fake_args = argparse.Namespace(
        title=args.title,
        status=status,
        tag=args.tag,
        file=args.file,
        decision=args.decision,
        question=args.question,
        next_step=args.next_step,
        summary=args.summary,
        summary_file=args.summary_file,
    )
    summary = read_summary(fake_args)
    note_path.write_text(build_note(fake_args, timestamp, summary), encoding="utf-8")
    rebuild_index(conversations_root)
    return note_path


def collect_start_files(memory_root: Path) -> list[str]:
    paths = [
        memory_root / "README.md",
        memory_root / "project-summary.md",
        memory_root / "current-state.md",
        memory_root / "decisions.md",
        memory_root / "open-questions.md",
        memory_root / "conversations" / "index.md",
    ]
    return [str(path) for path in paths if path.exists()]


def main() -> None:
    args = parse_args()
    start = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    root = Path(args.root).resolve() if args.root else find_project_root(start)
    memory_root = ensure_bootstrap(root, args.project_name)
    agents_path = ensure_agents_file(root)
    result: dict[str, object] = {
        "mode": args.mode,
        "project_root": str(root),
        "memory_root": str(memory_root),
        "agents_path": str(agents_path),
        "read_first": collect_start_files(memory_root),
    }

    if args.mode in {"checkpoint", "finish"}:
        result["note_path"] = str(record_note(args, root, memory_root))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"project_root={root}")
    print(f"memory_root={memory_root}")
    print(f"agents_path={agents_path}")
    if "note_path" in result:
        print(f"note_path={result['note_path']}")
    print("read_first:")
    for path in result["read_first"]:
        print(path)


if __name__ == "__main__":
    main()
