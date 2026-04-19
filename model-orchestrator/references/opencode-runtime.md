# OpenCode Runtime

Use this file when the orchestration design should be executable through OpenCode rather than staying at the policy level.

## Key Decision

If Gemini should be your primary stack, use:

- direct Gemini provider for main reasoning lanes
- OpenCode Go only for cheap fallback workers

Do not invert that relationship.

`OpenCode Go` is a low-cost curated open-model plan. As of April 16, 2026, its documented model list is GLM-5/5.1, Kimi K2.5, MiMo-V2-Pro/Omni, MiniMax M2.5/M2.7, and Qwen3.5/3.6 Plus. It does not expose Gemini models. OpenCode documents it as a normal provider with model IDs in the `opencode-go/<model-id>` format.

## Why OpenCode Fits This Skill

OpenCode supports:

- project-level `opencode.json` model routing
- `model` and `small_model` globals
- per-agent model overrides
- direct provider wiring
- non-interactive `opencode run`
- a server mode for repeated automation

That makes it a practical runtime for multi-model orchestration.

## Recommended Stack

### Gemini-first default

Use this when you want Google models to do most of the real work.

- `orchestrator`: `google/gemini-2.5-pro`
- `fast_worker`: `google/gemini-2.5-flash`
- `budget_worker`: `google/gemini-2.5-flash-lite`
- optional fallback `budget_worker`: `opencode-go/qwen3.5-plus` or `opencode-go/minimax-m2.5`

### Mixed fallback stack

Use this when Gemini is primary but you want a cheap non-Google lane during bursts or outages.

- `orchestrator`: `google/gemini-2.5-pro`
- `fast_worker`: `google/gemini-2.5-flash`
- `budget_worker`: `google/gemini-2.5-flash-lite`
- `overflow_budget_worker`: `opencode-go/qwen3.5-plus`
- `overflow_fast_worker`: `opencode-go/kimi-k2.5` or `opencode-go/qwen3.6-plus`

## Direct Gemini in OpenCode

OpenCode can route models by provider and agent. The cleanest layout is:

1. Configure Google Gemini as the main provider.
2. Set global `model` and `small_model`.
3. Override specific agents only when you want a different lane.

Example project config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "google": {
      "options": {
        "apiKey": "{env:GEMINI_API_KEY}"
      },
      "models": {
        "gemini-2.5-pro": {},
        "gemini-2.5-flash": {},
        "gemini-2.5-flash-lite": {}
      }
    },
    "opencode-go": {}
  },
  "model": "google/gemini-2.5-flash",
  "small_model": "google/gemini-2.5-flash-lite",
  "agent": {
    "plan": {
      "model": "google/gemini-2.5-pro"
    },
    "build": {
      "model": "google/gemini-2.5-flash"
    },
    "review": {
      "model": "google/gemini-2.5-pro"
    },
    "background": {
      "model": "google/gemini-2.5-flash-lite"
    }
  }
}
```

Inference:

- `plan` acts like `orchestrator`
- `build` acts like `fast_worker`
- `background` acts like `budget_worker`
- `review` acts like `verifier` or `reasoner`

If your OpenCode install already exposes Google models without explicit model entries, you can simplify the `provider.google` block. Keep the explicit version only when you want deterministic available model IDs in the project config.

## Gemini Cost and Latency Notes

Current official Gemini guidance makes these defaults sensible:

- `gemini-2.5-pro` for hard reasoning and coding with large-context synthesis
- `gemini-2.5-flash` for general price-performance execution
- `gemini-2.5-flash-lite` for cheapest high-throughput preprocessing

`gemini-2.5-flash` supports configurable thinking budgets, while `gemini-2.5-pro` is the stronger high-end lane and cannot simply be treated as "Flash but bigger."

If you need lower latency on `gemini-2.5-flash`, tune provider-specific options rather than swapping your whole routing policy.

## OpenCode Go Fallback

Use OpenCode Go when:

- Gemini rate limits spike
- you want a cheap overflow lane
- a subtask is reversible and high-volume
- you want open-model workers without wiring multiple vendors yourself

Example routing idea:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "google": {
      "options": {
        "apiKey": "{env:GEMINI_API_KEY}"
      },
      "models": {
        "gemini-2.5-pro": {},
        "gemini-2.5-flash": {},
        "gemini-2.5-flash-lite": {}
      }
    },
    "opencode-go": {}
  },
  "model": "google/gemini-2.5-flash",
  "small_model": "google/gemini-2.5-flash-lite",
  "agent": {
    "plan": {
      "model": "google/gemini-2.5-pro"
    },
    "extract": {
      "model": "google/gemini-2.5-flash-lite"
    },
    "overflow-extract": {
      "model": "opencode-go/qwen3.5-plus"
    },
    "overflow-solve": {
      "model": "opencode-go/kimi-k2.5"
    }
  }
}
```

This keeps Gemini primary and uses Go only where quality risk is acceptable.

## Execution Patterns

### Run one-off tasks

```powershell
opencode run -m google/gemini-2.5-flash "Summarize the touched files and propose a patch plan."
```

### Run a high-end synthesis pass

```powershell
opencode run -m google/gemini-2.5-pro "Compare these candidate fixes and choose the safest one."
```

### Run a cheap preprocessing pass

```powershell
opencode run -m google/gemini-2.5-flash-lite "Extract repeated stack traces and cluster duplicate failures."
```

### Run an OpenCode Go overflow worker

```powershell
opencode run -m opencode-go/qwen3.5-plus "Classify these 200 log snippets by failure type."
```

## Authentication Guidance

Prefer environment variables over plain text files.

Example PowerShell session setup:

```powershell
$env:GEMINI_API_KEY="your-key-here"
opencode
```

Do not keep live API keys in files like `gemini api.txt`. Rotate the key if it has been shared or committed anywhere.

## Windows Note

OpenCode can run directly on Windows, but the official docs recommend WSL for the best experience on Windows. If your orchestration starts to rely on deeper shell workflows, repo tools, or background agents, prefer WSL.

## Practical Recommendation

For your stated goal, the simplest durable setup is:

1. Gemini direct for `orchestrator`, `fast_worker`, and `budget_worker`
2. OpenCode Go only as a fallback worker pool
3. Per-agent OpenCode overrides for lanes that need explicit model control
4. Secrets only through env vars or OpenCode auth storage
