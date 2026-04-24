---
name: codex-cost-aware-workflow
description: Set up and maintain a Windows Codex cost-aware workflow with RTK terminal-output compression, an OpenCode Go cheap-ai read-only subagent CLI, and AGENTS.md rules. Use when the user wants Codex to stay the main orchestrator while delegating low-risk summaries, test ideas, edge-case discovery, documentation drafts, or isolated code explanations to cheaper models.
---

# Codex Cost Aware Workflow

## Core Rule

Keep Codex as the supervising agent. Use cheaper tools only as helpers:

- RTK wraps noisy shell commands and compresses long output.
- `tools/cheap-ai.mjs` calls OpenCode Go models for read-only helper analysis.
- `AGENTS.md` records the project policy so future threads use the same workflow.

Do not let cheap models edit files, make final architecture calls, review security-sensitive code, handle secrets, or become the source of truth.

## Setup Workflow

For a project setup request, run:

```powershell
python "$env:USERPROFILE\.codex\skills\codex-cost-aware-workflow\scripts\setup_cost_aware_workflow.py" --root "C:\path\to\project"
```

Use `--smoke-test` after setup to verify local wiring. Use `--live-smoke` only when `OPENCODE_API_KEY` is set and the user expects a real OpenCode Go request.

Use `--install-rtk` only when the user explicitly wants the script to install RTK. Otherwise, report missing RTK and show the install command or release path.

## What The Script Does

The setup script:

- verifies `node`, `npm`, and `git`
- ensures `%USERPROFILE%\.codex` exists
- checks `OPENCODE_API_KEY` without printing it
- checks RTK via `rtk --version` and `rtk gain`
- optionally installs RTK on Windows from `rtk-ai/rtk` releases
- writes `tools/cheap-ai.mjs` into the target project
- adds a managed cost-aware block to project `AGENTS.md`
- adds a short managed global policy to `%USERPROFILE%\.codex\AGENTS.md`
- never stores API keys in repo files

## Operating Policy

Use RTK-wrapped commands when output may be long:

```powershell
rtk git status
rtk git diff
rtk rg "pattern" .
rtk npm test
rtk pnpm build
rtk tsc
```

Use cheap-ai only for read-only subtasks:

```powershell
node tools\cheap-ai.mjs --model qwen3.6-plus --task "Suggest unit tests for this file." --files "src/auth.ts"
```

Good cheap-ai tasks: summarize long files, suggest tests, find edge cases, draft docs, explain isolated functions, compare low-risk refactor options.

Keep Codex direct for: implementation, final review, security, auth, payments, migrations, destructive operations, production deployment, dependency upgrades, and complex debugging.

## Model Defaults

Default to `qwen3.6-plus` for general cheap coding analysis.

Try `kimi-k2.6`, `glm-5.1`, or `mimo-v2-pro` for coding-heavy analysis when the default is weak or rate-limited.

Use `minimax-m2.7` or `minimax-m2.5` only when the MiniMax `messages` endpoint is explicitly useful or needs testing.

Open `references/provider-notes.md` only when checking current endpoint details, model lists, RTK Windows behavior, or troubleshooting provider setup.
