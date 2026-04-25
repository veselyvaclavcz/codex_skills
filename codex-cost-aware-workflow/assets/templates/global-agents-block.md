<!-- COST-AWARE-CODEX-GLOBAL:BEGIN -->
# Global cost-aware Codex policy

Keep the main Codex session as the senior orchestrator.

This is the default operating policy for substantial project work. Treat this file as standing user permission to use cost-aware orchestration when the criteria below match; the user should not need to repeat the prompt manually.

Use custom Codex subagents only for bounded low-risk work:
- `explorer-fast`: read-only codebase reconnaissance
- `worker-cheap`: small localized changes
- `reviewer-mini`: focused diff review
- `summarizer-nano`: logs, docs, extraction, long-output summaries

Subagents are not free. Use them when they isolate context or reduce main-model work, not for every trivial step.

Default routing:
- For substantial codebase exploration, spawn `explorer-fast` before making a plan.
- For a small, localized, clearly specified change, consider `worker-cheap`.
- After non-trivial edits, consider `reviewer-mini` for a focused diff review.
- For long logs, docs, or command output, use `summarizer-nano` or RTK compression.

Do not use subagents for tiny one-step tasks, ambiguous work, or high-risk decisions.
Use at most 2-3 subagents unless the user explicitly asks for broader parallel work.

Prefer RTK-wrapped shell commands for long outputs.
Final edits, final review, architecture, security, auth, payments, migrations, and destructive operations stay with the main Codex session.
<!-- COST-AWARE-CODEX-GLOBAL:END -->
