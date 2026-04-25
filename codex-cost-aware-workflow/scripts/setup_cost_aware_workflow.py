#!/usr/bin/env python3
"""Set up a cost-aware Codex custom-subagent workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"
AGENT_TEMPLATES = TEMPLATES / "agents"
PROJECT_BEGIN = "<!-- COST-AWARE-CODEX:BEGIN -->"
PROJECT_END = "<!-- COST-AWARE-CODEX:END -->"
GLOBAL_BEGIN = "<!-- COST-AWARE-CODEX-GLOBAL:BEGIN -->"
GLOBAL_END = "<!-- COST-AWARE-CODEX-GLOBAL:END -->"


AGENT_FILES = [
    "explorer-fast.toml",
    "worker-cheap.toml",
    "reviewer-mini.toml",
    "summarizer-nano.toml",
]


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        return proc.returncode, (proc.stdout or "").strip()
    except FileNotFoundError:
        return 127, f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, f"{' '.join(cmd)} timed out"


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str, force: bool = True) -> bool:
    if path.exists() and not force:
        return False
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def update_managed_block(path: Path, block: str, begin: str, end: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    block = block.strip() + "\n"

    if begin in existing and end in existing:
        before = existing.split(begin, 1)[0].rstrip()
        after = existing.split(end, 1)[1].lstrip()
        new_content = "\n\n".join(part for part in [before, block, after.rstrip()] if part) + "\n"
        action = "updated"
    else:
        new_content = existing.rstrip()
        if new_content:
            new_content += "\n\n"
        new_content += block
        action = "created" if not existing else "appended"

    if new_content != existing:
        path.write_text(new_content, encoding="utf-8", newline="\n")
    else:
        action = "unchanged"
    return action


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def check_environment(root: Path) -> list[str]:
    messages: list[str] = []
    for name in ["node", "npm", "git"]:
        exe = shutil.which(name)
        if not exe:
            messages.append(f"MISS {name}: not found in PATH")
            continue
        code, out = run([exe, "--version"], cwd=root)
        first = out.splitlines()[0] if out else "no output"
        messages.append(f"OK   {name}: {first} ({exe})" if code == 0 else f"WARN {name}: {first}")

    codex_dir = Path.home() / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    messages.append(f"OK   codex dir: {codex_dir}")

    if command_available("rtk"):
        for cmd in [["rtk", "--version"], ["rtk", "gain"]]:
            code, out = run(cmd, cwd=root)
            first = out.splitlines()[0] if out else "no output"
            messages.append(f"OK   {' '.join(cmd)}: {first}" if code == 0 else f"WARN {' '.join(cmd)}: {first}")
    else:
        messages.append("MISS rtk: install from https://github.com/rtk-ai/rtk/releases or run this script with --install-rtk")

    return messages


def install_rtk_windows() -> str:
    if os.name != "nt":
        return "SKIP RTK auto-install: --install-rtk currently supports Windows only. Use cargo install --git https://github.com/rtk-ai/rtk"

    api_url = "https://api.github.com/repos/rtk-ai/rtk/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "codex-cost-aware-workflow"})
    with urllib.request.urlopen(req, timeout=60) as res:
        release = json.loads(res.read().decode("utf-8"))

    asset = next(
        (a for a in release.get("assets", []) if a.get("name") == "rtk-x86_64-pc-windows-msvc.zip"),
        None,
    )
    if not asset:
        return "FAIL RTK auto-install: release asset rtk-x86_64-pc-windows-msvc.zip was not found"

    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / asset["name"]
        urllib.request.urlretrieve(asset["browser_download_url"], zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            members = [m for m in zf.namelist() if m.lower().endswith("rtk.exe")]
            if not members:
                return "FAIL RTK auto-install: rtk.exe was not in the release archive"
            with zf.open(members[0]) as src, (bin_dir / "rtk.exe").open("wb") as dst:
                shutil.copyfileobj(src, dst)

    user_path = os.environ.get("Path", "")
    bin_text = str(bin_dir)
    if bin_text.lower() not in user_path.lower():
        new_path = f"{user_path};{bin_text}" if user_path else bin_text
        ps = f"[Environment]::SetEnvironmentVariable('Path', {json.dumps(new_path)}, 'User')"
        run(["powershell", "-NoProfile", "-Command", ps])
        os.environ["Path"] = new_path

    return f"OK   RTK installed to {bin_dir}. Restart terminal if rtk is still not found."


def set_toml_key(text: str, table: str, key: str, value: str) -> str:
    header = f"[{table}]"
    table_re = re.compile(rf"(?ms)^\[{re.escape(table)}\]\s*$.*?(?=^\[|\Z)")
    match = table_re.search(text)

    line = f"{key} = {value}"
    if not match:
        suffix = "" if text.endswith("\n") or not text else "\n"
        return f"{text}{suffix}\n{header}\n{line}\n"

    block = match.group(0).rstrip()
    key_re = re.compile(rf"(?m)^{re.escape(key)}\s*=.*$")
    if key_re.search(block):
        new_block = key_re.sub(line, block)
    else:
        new_block = block + "\n" + line
    return text[: match.start()] + new_block + "\n" + text[match.end() :]


def merge_config(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    desired = [
        ("features", "multi_agent", "true"),
        ("agents", "max_threads", "3"),
        ("agents", "max_depth", "1"),
        ("agents", "job_max_runtime_seconds", "1200"),
        ("profiles.deep", "model", '"gpt-5.5"'),
        ("profiles.deep", "model_reasoning_effort", '"high"'),
        ("profiles.deep", "model_verbosity", '"medium"'),
        ("profiles.balanced", "model", '"gpt-5.4"'),
        ("profiles.balanced", "model_reasoning_effort", '"medium"'),
        ("profiles.balanced", "model_verbosity", '"low"'),
        ("profiles.fast", "model", '"gpt-5.4-mini"'),
        ("profiles.fast", "model_reasoning_effort", '"low"'),
        ("profiles.fast", "model_verbosity", '"low"'),
    ]

    for table, key, value in desired:
        text = set_toml_key(text, table, key, value)

    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if text != original:
        path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
        return "updated" if original else "created"
    return "unchanged"


def install_agent_templates(target_dir: Path, force: bool) -> list[str]:
    messages: list[str] = []
    for name in AGENT_FILES:
        src = AGENT_TEMPLATES / name
        dst = target_dir / name
        changed = write_if_changed(dst, src.read_text(encoding="utf-8"), force=force)
        messages.append(("WROTE" if changed else "OK   ") + f" {dst}")
    return messages


def setup_project(root: Path, force: bool) -> list[str]:
    messages: list[str] = []
    codex_dir = root / ".codex"
    messages.append(f"{merge_config(codex_dir / 'config.toml').upper():7} {codex_dir / 'config.toml'}")
    messages.extend(install_agent_templates(codex_dir / "agents", force=force))

    project_agents = root / "AGENTS.md"
    action = update_managed_block(
        project_agents,
        read_template("project-agents-block.md"),
        PROJECT_BEGIN,
        PROJECT_END,
    )
    messages.append(f"{action.upper():7} {project_agents}")
    return messages


def setup_global(force: bool) -> list[str]:
    messages: list[str] = []
    codex_dir = Path.home() / ".codex"
    messages.append(f"{merge_config(codex_dir / 'config.toml').upper():7} {codex_dir / 'config.toml'}")
    messages.extend(install_agent_templates(codex_dir / "agents", force=force))

    global_agents = codex_dir / "AGENTS.md"
    action = update_managed_block(
        global_agents,
        read_template("global-agents-block.md"),
        GLOBAL_BEGIN,
        GLOBAL_END,
    )
    messages.append(f"{action.upper():7} {global_agents}")
    return messages


def smoke_test(root: Path, label: str) -> list[str]:
    messages: list[str] = []
    messages.append(f"Smoke target ({label}): {root}")
    if command_available("rtk"):
        for cmd in [["rtk", "--version"], ["rtk", "gain"], ["rtk", "git", "status"]]:
            code, out = run(cmd, cwd=root)
            first = out.splitlines()[0] if out else "no output"
            status = "OK  " if code == 0 else "WARN"
            messages.append(f"{status} {' '.join(cmd)}: {first}")

    toml_files = [
        root / ".codex" / "config.toml",
        *(root / ".codex" / "agents" / name for name in AGENT_FILES),
    ]
    for path in toml_files:
        if not path.exists():
            messages.append(f"WARN missing: {path}")
            continue
        code, out = run(
            [
                sys.executable,
                "-c",
                "import pathlib,tomllib,sys; tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))",
                str(path),
            ],
            cwd=root,
        )
        status = "OK  " if code == 0 else "WARN"
        messages.append(f"{status} TOML {path.name}: {out or 'valid'}")

    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up RTK and Codex custom subagents for cost-aware work.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--scope", choices=["project", "global", "both"], default="project", help="Where to install config and custom agents.")
    parser.add_argument("--check-only", action="store_true", help="Only check environment; do not write project files.")
    parser.add_argument("--install-rtk", action="store_true", help="Install RTK from rtk-ai/rtk releases on Windows.")
    parser.add_argument("--no-force", action="store_true", help="Do not overwrite existing agent TOML files.")
    parser.add_argument("--smoke-test", action="store_true", help="Run local smoke tests after setup.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"FAIL project root does not exist: {root}", file=sys.stderr)
        return 2

    print(f"Project root: {root}")
    for msg in check_environment(root):
        print(msg)

    if args.install_rtk:
        print(install_rtk_windows())

    if not args.check_only:
        if args.scope in {"project", "both"}:
            for msg in setup_project(root, force=not args.no_force):
                print(msg)
        if args.scope in {"global", "both"}:
            for msg in setup_global(force=not args.no_force):
                print(msg)

    if args.smoke_test:
        if args.scope in {"project", "both"}:
            for msg in smoke_test(root, "project"):
                print(msg)
        if args.scope in {"global", "both"}:
            for msg in smoke_test(Path.home(), "global"):
                print(msg)

    if command_available("rtk"):
        print("NEXT Use RTK-wrapped commands for long shell output.")
    else:
        print("NEXT Install RTK, then run: rtk init -g --codex")
    print("NEXT AGENTS.md is the standing routing policy. Explicit prompts are only needed when you want to force a specific subagent path.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
