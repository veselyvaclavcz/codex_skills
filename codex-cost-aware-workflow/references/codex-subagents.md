# Codex Subagents Notes

Use this reference when setup needs current Codex custom-agent behavior, model choices, or caveats.

## Official behavior

OpenAI Codex docs describe subagent workflows as parallel agent threads that Codex can spawn, route, wait on, and consolidate. Current Codex releases enable subagent workflows by default.

Codex only spawns subagents when explicitly asked. Subagent activity is surfaced in the Codex app and CLI. Subagents do their own model and tool work, so they still consume usage.

Custom agents live in:

- `%USERPROFILE%\.codex\agents\*.toml` for global personal agents
- `.codex\agents\*.toml` for project-scoped agents

Required fields:

- `name`
- `description`
- `developer_instructions`

Optional useful fields:

- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `nickname_candidates`
- `mcp_servers`
- `skills.config`

`name` is the source of truth, even when the filename differs.

## Model choices

OpenAI model docs describe `gpt-5.5` as the flagship model for complex reasoning and coding. They describe `gpt-5.4-mini` and `gpt-5.4-nano` as lower-latency, lower-cost variants, and `gpt-5.4-mini` as useful for coding, computer use, and subagents.

Default recommendation:

- Main session: use the newest/highest-capability model available in the Codex app model picker.
- `explorer-fast`: `gpt-5.4-mini`, low reasoning
- `worker-cheap`: `gpt-5.4-mini`, medium reasoning
- `reviewer-mini`: `gpt-5.4-mini`, medium reasoning
- `summarizer-nano`: `gpt-5.4-nano`, low reasoning

If `gpt-5.4-nano` is not available in the local Codex app, change `summarizer-nano` to `gpt-5.4-mini`.

## Known caveats

There is no single `auto_downscale = true` setting. Use config, custom agents, AGENTS.md, and explicit prompts.

Subagents are cost controls only when the delegated prompt is smaller than the main context and the task is easy to verify.

Some Codex runtimes can differ in how they expose named custom agents. If a custom agent cannot be invoked by name, use built-in `explorer` or `worker` roles and include the intended custom-agent instructions in the spawned prompt.
