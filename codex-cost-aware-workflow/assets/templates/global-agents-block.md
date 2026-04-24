<!-- COST-AWARE-CODEX-GLOBAL:BEGIN -->
# Global cost-aware policy

Prefer RTK-wrapped shell commands for long outputs.

When a project contains `tools/cheap-ai.mjs`, Codex may use it as a read-only low-cost subagent for summarization, test suggestions, edge-case discovery, documentation drafts, and isolated code explanations.

Never let cheap-ai modify files.
Final edits and review must be done by Codex.
Never store `OPENCODE_API_KEY` or any other API key in a repository, `AGENTS.md`, or documentation file.
<!-- COST-AWARE-CODEX-GLOBAL:END -->
