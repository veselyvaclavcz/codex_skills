<!-- COST-AWARE-CODEX-GLOBAL:BEGIN -->
# Global cost-aware Codex policy

Keep the main Codex session as the senior orchestrator.

Use custom Codex subagents only for bounded low-risk work:
- `explorer-fast`: read-only codebase reconnaissance
- `worker-cheap`: small localized changes
- `reviewer-mini`: focused diff review
- `summarizer-nano`: logs, docs, extraction, long-output summaries

Subagents are not free. Use them when they isolate context or reduce main-model work, not for every trivial step.

Prefer RTK-wrapped shell commands for long outputs.
Final edits, final review, architecture, security, auth, payments, migrations, and destructive operations stay with the main Codex session.
<!-- COST-AWARE-CODEX-GLOBAL:END -->
