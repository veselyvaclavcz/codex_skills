<!-- COST-AWARE-CODEX:BEGIN -->
# Cost-aware Codex orchestration

## Core principle

The main Codex session is the senior orchestrator.

Use the main model for:
- task planning
- architecture
- security-sensitive decisions
- final implementation decisions
- final diff review
- integration of subagent results
- anything ambiguous or high-risk

Use cheaper subagents only for bounded subtasks.

## Subagent routing policy

Prefer these subagents:

- `explorer-fast` for read-only codebase exploration, file discovery, execution path tracing, symbol mapping, and impact analysis.
- `worker-cheap` for small, localized, low-risk implementation tasks only after the parent has defined the task clearly.
- `reviewer-mini` for low-cost review of diffs, missing tests, regressions, and edge cases.
- `summarizer-nano` for summarizing logs, long docs, command outputs, and extracting simple structured facts.

Do not use subagents for very small one-step tasks.
Use at most 2-3 subagents unless the user explicitly asks for broader parallel exploration.

## Model cost rule

Preserve the main high-capability model for reasoning, planning, synthesis, and final decisions.

Delegate only work that is:
- well scoped
- low risk
- easy to verify
- read-only or narrowly localized
- not security-sensitive

## RTK shell policy

Prefer RTK-wrapped commands whenever shell output may be long.

Use:
- `rtk git status`
- `rtk git diff`
- `rtk git log`
- `rtk rg "<pattern>" .`
- `rtk find "<pattern>" .`
- `rtk npm test`
- `rtk pnpm test`
- `rtk npm run build`
- `rtk pnpm build`
- `rtk tsc`
- `rtk docker logs`

Avoid raw long-output commands unless full output is explicitly needed.

## Verification rule

After using a subagent:

1. Summarize its useful findings.
2. Identify uncertainty.
3. Verify against actual code.
4. Apply or reject the suggestion as the main Codex agent.
5. Run targeted checks through RTK.

## Practical prompt

Use this when you want explicit cost-aware orchestration:

```text
Use cost-aware workflow from AGENTS.md.
Keep the main model as orchestrator and reviewer.
Use explorer-fast for reconnaissance.
If the implementation is small and clear, delegate it to worker-cheap.
Use reviewer-mini for focused diff review.
Use RTK for shell commands.
Final decisions stay with the main agent.
```
<!-- COST-AWARE-CODEX:END -->
