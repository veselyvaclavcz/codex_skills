<!-- COST-AWARE-CODEX:BEGIN -->
# Cost-aware Codex workflow

## Core principle

Codex remains the main orchestrator, reasoning layer, final editor, and reviewer.

Use cheaper tools only for low-risk helper work:
- RTK reduces noisy command output.
- `tools/cheap-ai.mjs` delegates small read-only subtasks to OpenCode Go models.

Never let the cheap model directly modify files.
Treat cheap model output as advisory only.
Codex must verify all conclusions before editing code.

## When to use Codex directly

Use Codex directly for:
- architecture decisions
- security-sensitive changes
- final implementation
- editing files
- reviewing diffs
- debugging complex failures
- dependency upgrades
- production-impacting decisions
- credentials, auth, payment, permissions, data deletion, or migrations

## Use RTK for shell commands

Prefer RTK-wrapped commands whenever command output may be long.

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
If RTK reports that full raw output was saved to a file, inspect the relevant part of that saved output instead of rerunning the whole command.

## Use OpenCode Go cheap subagent for low-risk subtasks

Use the cheap subagent only for read-only analysis:

```powershell
node tools\cheap-ai.mjs --model qwen3.6-plus --task "TASK" --files "file1,file2"
```

Good use cases:
- summarize a long file
- propose unit tests
- identify edge cases
- explain an isolated function
- draft documentation
- suggest refactoring options
- compare two possible approaches
- generate a checklist for manual review

Do not use cheap-ai for:
- writing directly to files
- applying patches
- final code review
- security-sensitive logic
- auth
- payments
- migrations
- secrets
- destructive operations
- production deployment

## Recommended default models

Default:
- `qwen3.6-plus`

Try for coding-heavy analysis:
- `kimi-k2.6`
- `glm-5.1`
- `mimo-v2-pro`

Try only when explicitly useful:
- `minimax-m2.7`
- `minimax-m2.5`

## Verification rule

After using cheap-ai:

1. Summarize what it suggested.
2. Identify what is useful and what is uncertain.
3. Verify against the actual code.
4. Apply changes manually through Codex only if they make sense.
5. Run tests using RTK-wrapped commands.
<!-- COST-AWARE-CODEX:END -->
