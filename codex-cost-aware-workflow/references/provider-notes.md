# Provider Notes

Use this file only when setup requires provider details or troubleshooting.

## OpenCode Go

OpenCode Go is a low-cost subscription for open coding models. The public docs describe it as beta and list these model IDs for API use:

- `glm-5.1`
- `glm-5`
- `kimi-k2.5`
- `kimi-k2.6`
- `mimo-v2-pro`
- `mimo-v2-omni`
- `mimo-v2.5-pro`
- `mimo-v2.5`
- `minimax-m2.7`
- `minimax-m2.5`
- `qwen3.6-plus`
- `qwen3.5-plus`

Use `https://opencode.ai/zen/go/v1/chat/completions` for GLM, Kimi, MiMo, and Qwen models.

Use `https://opencode.ai/zen/go/v1/messages` for MiniMax models.

OpenCode config may use `opencode-go/<model-id>`, but direct API calls should first try the plain model ID. If a smoke test fails with an unknown-model error, retry once with the prefixed ID and record the working format in project notes.

## RTK

Install the RTK project from `rtk-ai/rtk`. Do not assume `cargo install rtk` is correct, because the RTK docs warn about a crates.io name collision.

Useful verification commands:

```powershell
rtk --version
rtk gain
rtk git status
```

Codex integration:

```powershell
rtk init -g --codex
```

On native Windows, RTK filters work from PowerShell or cmd.exe, but auto-rewrite hooks are limited. Prefer explicit `rtk ...` commands unless running in WSL.
