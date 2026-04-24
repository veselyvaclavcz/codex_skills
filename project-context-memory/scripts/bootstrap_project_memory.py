#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
AGENTS_BEGIN = "<!-- PROJECT-CONTEXT-MEMORY:BEGIN -->"
AGENTS_END = "<!-- PROJECT-CONTEXT-MEMORY:END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap shared project memory files.")
    parser.add_argument("--root", required=True, help="Project root directory.")
    parser.add_argument("--project-name", help="Optional project name override.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite starter files if they already exist.",
    )
    return parser.parse_args()


def render_template(name: str, replacements: dict[str, str]) -> str:
    path = TEMPLATE_DIR / name
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def write_if_missing(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


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
        "Use `$codex-cost-aware-workflow` when RTK or read-only cheap-ai delegation is actually worth it.\n\n"
        "Prefer this split:\n"
        "- Keep final planning, risky decisions, and user-facing synthesis in Codex.\n"
        "- Use `tools/cheap-ai.mjs` for bounded, read-only subtasks when that saves time or tokens.\n"
        "- Do not delegate trivial work or tasks whose value is mostly in integration.\n\n"
        "Default delegated tasks:\n"
        "- summaries, test ideas, edge cases, documentation drafts, and isolated code explanations\n"
        "- OpenCode Go models such as `qwen3.6-plus`, `kimi-k2.6`, `glm-5.1`, or `mimo-v2-pro`\n\n"
        "Token discipline:\n"
        "- Do not forward the whole conversation by default.\n"
        "- Send only the minimal context, artifacts, and acceptance criteria needed for the delegated subtask.\n"
        "- Treat cheap-ai output as advisory; Codex keeps final edits and review.\n"
        f"{AGENTS_END}\n"
    )


def ensure_agents_file(root: Path, force: bool) -> None:
    agents_path = root / "AGENTS.md"
    managed_block = build_agents_block(root)
    if not agents_path.exists():
        agents_path.write_text(
            "# AGENTS\n\n"
            "This file contains repository-specific operating rules for Codex and related agents.\n\n"
            + managed_block,
            encoding="utf-8",
        )
        return

    existing = agents_path.read_text(encoding="utf-8")
    if AGENTS_BEGIN in existing and AGENTS_END in existing:
        updated = re.sub(
            rf"{re.escape(AGENTS_BEGIN)}.*?{re.escape(AGENTS_END)}\n?",
            managed_block,
            existing,
            flags=re.DOTALL,
        )
        agents_path.write_text(updated, encoding="utf-8")
        return

    if force:
        agents_path.write_text(existing.rstrip() + "\n\n" + managed_block, encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")

    project_name = args.project_name or root.name
    memory_root = root / "docs" / "project-memory"
    conversations_root = memory_root / "conversations"
    year_root = conversations_root / f"{datetime.now().year:04d}"
    year_root.mkdir(parents=True, exist_ok=True)

    replacements = {
        "PROJECT_NAME": project_name,
        "PROJECT_ROOT": str(root),
        "MEMORY_ROOT": str(memory_root),
    }

    files = {
        memory_root / "README.md": render_template("README.md.tmpl", replacements),
        memory_root / "project-summary.md": render_template("project-summary.md.tmpl", replacements),
        memory_root / "current-state.md": render_template("current-state.md.tmpl", replacements),
        memory_root / "decisions.md": render_template("decisions.md.tmpl", replacements),
        memory_root / "open-questions.md": render_template("open-questions.md.tmpl", replacements),
        memory_root / "conventions.md": render_template("conventions.md.tmpl", replacements),
        conversations_root / "index.md": render_template("conversations-index.md.tmpl", replacements),
        memory_root / "memory.json": json.dumps(
            {
                "project_name": project_name,
                "project_root": str(root),
                "memory_root": str(memory_root),
                "schema_version": 1,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    }

    for path, content in files.items():
        write_if_missing(path, content, args.force)

    ensure_agents_file(root, args.force)

    print(memory_root)


if __name__ == "__main__":
    main()
