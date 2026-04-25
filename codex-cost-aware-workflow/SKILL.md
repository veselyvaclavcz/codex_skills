---
name: codex-cost-aware-workflow
description: Set up and operate a cost-aware Codex workflow using Codex custom subagents and RTK. Use when the user wants the main Codex model to stay the senior orchestrator while cheaper Codex subagents handle bounded exploration, small implementation tasks, reviews, summaries, logs, and extraction work with explicit routing rules in AGENTS.md.
---

# Codex Cost Aware Workflow

## Core Rule

Keep the main Codex session as the senior orchestrator. Use subagents only for bounded work that is easy to verify.

This skill does not rely on an `auto_downscale` switch. Codex does not automatically route every turn to cheaper models just because a config file exists. The practical pattern is:

- main session: planning, architecture, integration, final edits, final review
- custom subagents: scoped exploration, small changes, review, summarization
- RTK: compress long shell output
- `AGENTS.md`: remind future threads how to route work

Subagents still consume Codex usage. Use them to isolate context and save main-model attention, not for every small one-step task.

## Setup Workflow

For a project setup request, run:

```powershell
python "$env:USERPROFILE\.codex\skills\codex-cost-aware-workflow\scripts\setup_cost_aware_workflow.py" --root "C:\path\to\project" --scope project --smoke-test
```

Use `--scope global` to install the same custom agents under `%USERPROFILE%\.codex\agents`.

Use `--install-rtk` only when RTK is missing and the user wants the script to install it from `rtk-ai/rtk`.

## What The Script Writes

Project scope writes:

- `.codex/config.toml` with multi-agent enabled and conservative subagent limits
- `.codex/agents/explorer-fast.toml`
- `.codex/agents/worker-cheap.toml`
- `.codex/agents/reviewer-mini.toml`
- `.codex/agents/summarizer-nano.toml`
- `AGENTS.md` managed cost-aware block

Global scope writes:

- `%USERPROFILE%\.codex\agents\*.toml`
- `%USERPROFILE%\.codex\config.toml` multi-agent limits and optional profiles
- `%USERPROFILE%\.codex\AGENTS.md` managed cost-aware block

Do not overwrite unrelated user rules outside managed blocks.

## Routing Policy

Use the main model directly for:

- task planning
- architecture
- security-sensitive decisions
- final implementation decisions
- final diff review
- integration of subagent results
- anything ambiguous or high-risk

Use subagents only when the work is well scoped, low risk, easy to verify, and benefits from isolated context.

Default routing:

- `explorer-fast`: read-only codebase exploration, file discovery, execution paths, symbols, tests
- `worker-cheap`: small, localized, low-risk code changes after the parent defines the exact task
- `reviewer-mini`: cost-efficient review for correctness, regressions, missing tests, edge cases
- `summarizer-nano`: logs, docs, long command output, simple extraction

Use at most `2-3` subagents unless the user explicitly asks for wider parallel work.

## Prompt Pattern

When the user asks for cost-aware work, use language like:

```text
I will keep the main session as orchestrator.
I will use explorer-fast for read-only reconnaissance.
If the change is small and clear, I will delegate it to worker-cheap.
I will use reviewer-mini for a focused diff review.
I will verify results myself before finalizing.
```

Do not pretend subagents were used. If no subagent was useful, say that and do the work directly.

## RTK Policy

Prefer RTK-wrapped commands whenever output may be long:

```powershell
rtk git status
rtk git diff
rtk git log
rtk rg "pattern" .
rtk find "pattern" .
rtk npm test
rtk pnpm test
rtk npm run build
rtk pnpm build
rtk tsc
rtk docker logs
```

Avoid raw long-output commands unless full output is explicitly needed.

## References

Open `references/codex-subagents.md` when checking current Codex custom-agent schema, model choices, config behavior, or known runtime caveats.
