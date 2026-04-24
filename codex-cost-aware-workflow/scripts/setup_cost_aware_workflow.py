#!/usr/bin/env python3
"""Set up a cost-aware Codex workflow for a project."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"
PROJECT_BEGIN = "<!-- COST-AWARE-CODEX:BEGIN -->"
PROJECT_END = "<!-- COST-AWARE-CODEX:END -->"
GLOBAL_BEGIN = "<!-- COST-AWARE-CODEX-GLOBAL:BEGIN -->"
GLOBAL_END = "<!-- COST-AWARE-CODEX-GLOBAL:END -->"


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        return proc.returncode, proc.stdout.strip()
    except FileNotFoundError:
        return 127, f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, f"{' '.join(cmd)} timed out"


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def write_text_if_changed(path: Path, content: str, force: bool = True) -> bool:
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

    if os.environ.get("OPENCODE_API_KEY"):
        messages.append("OK   OPENCODE_API_KEY: set")
    else:
        messages.append('MISS OPENCODE_API_KEY: set it with [Environment]::SetEnvironmentVariable("OPENCODE_API_KEY", "YOUR_KEY", "User")')

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


def setup_project(root: Path, skip_global_agents: bool, force: bool) -> list[str]:
    messages: list[str] = []
    cheap_ai_path = root / "tools" / "cheap-ai.mjs"
    changed = write_text_if_changed(cheap_ai_path, read_template("cheap-ai.mjs"), force=force)
    messages.append(("WROTE" if changed else "OK   ") + f" {cheap_ai_path}")

    project_agents = root / "AGENTS.md"
    action = update_managed_block(
        project_agents,
        read_template("project-agents-block.md"),
        PROJECT_BEGIN,
        PROJECT_END,
    )
    messages.append(f"{action.upper():5} {project_agents}")

    if not skip_global_agents:
        global_agents = Path.home() / ".codex" / "AGENTS.md"
        action = update_managed_block(
            global_agents,
            read_template("global-agents-block.md"),
            GLOBAL_BEGIN,
            GLOBAL_END,
        )
        messages.append(f"{action.upper():5} {global_agents}")

    return messages


def smoke_test(root: Path, live: bool) -> list[str]:
    messages: list[str] = []
    tests = [["node", "tools/cheap-ai.mjs", "--help"]]
    if command_available("rtk"):
        tests.extend([["rtk", "--version"], ["rtk", "gain"], ["rtk", "git", "status"]])

    for cmd in tests:
        code, out = run(cmd, cwd=root)
        first = out.splitlines()[0] if out else "no output"
        status = "OK  " if code == 0 else "WARN"
        messages.append(f"{status} {' '.join(cmd)}: {first}")

    if live:
        if not os.environ.get("OPENCODE_API_KEY"):
            messages.append("SKIP live smoke: OPENCODE_API_KEY is missing")
        else:
            code, out = run(
                ["node", "tools/cheap-ai.mjs", "--model", "qwen3.6-plus", "--task", "Return exactly: OK"],
                cwd=root,
            )
            first = out.splitlines()[0] if out else "no output"
            status = "OK  " if code == 0 else "WARN"
            messages.append(f"{status} live cheap-ai qwen3.6-plus: {first}")

    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up RTK and OpenCode Go cheap-ai workflow for Codex.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--check-only", action="store_true", help="Only check environment; do not write project files.")
    parser.add_argument("--install-rtk", action="store_true", help="Install RTK from rtk-ai/rtk releases on Windows.")
    parser.add_argument("--skip-global-agents", action="store_true", help="Do not update ~/.codex/AGENTS.md.")
    parser.add_argument("--no-force", action="store_true", help="Do not overwrite an existing tools/cheap-ai.mjs.")
    parser.add_argument("--smoke-test", action="store_true", help="Run local smoke tests after setup.")
    parser.add_argument("--live-smoke", action="store_true", help="Run a live OpenCode Go smoke test when the API key is set.")
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
        for msg in setup_project(root, args.skip_global_agents, force=not args.no_force):
            print(msg)

    if args.smoke_test or args.live_smoke:
        for msg in smoke_test(root, live=args.live_smoke):
            print(msg)

    if not os.environ.get("OPENCODE_API_KEY"):
        print("NEXT Set OPENCODE_API_KEY before live OpenCode Go calls.")
    if command_available("rtk"):
        print("NEXT Run: rtk init -g --codex")
    else:
        print("NEXT Install RTK, then run: rtk init -g --codex")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
