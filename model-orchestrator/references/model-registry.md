# Model Registry

Use this file when the task needs concrete model-role recommendations, provider mappings, or a normalized registry shape.

This reference is intentionally split into:

1. capability classes that stay stable over time
2. current example mappings that can be refreshed as models change

## Registry Schema

Represent models with a provider-agnostic record like this:

```yaml
models:
  - id: "openai/gpt-5.4-mini"
    provider: "openai"
    capability_class: "fast_worker"
    modalities: ["text", "image"]
    tool_support: ["functions", "web_search", "file_search", "computer_use"]
    latency_tier: "fast"
    cost_tier: "low"
    strengths: ["coding", "subagents", "document processing"]
    weaknesses: ["less reliable than orchestrator on ambiguous synthesis"]
    default_use_cases:
      - "codebase search and summarization"
      - "patch drafting"
      - "parallel subtask execution"
    fallback_to: "openai/gpt-5.4"
```

Keep routing logic bound to `capability_class`, not to `id`.

## Capability Classes

### `orchestrator`

Use for:

- planning
- integration
- final tradeoff decisions
- final review before user-visible output

Pick the strongest reliable reasoning model you have available.

### `reasoner`

Use for:

- architecture
- hard debugging
- ambiguous synthesis
- non-local code changes

This can be the same model as `orchestrator` if the stack is small.

### `fast_worker`

Use for:

- most delegated coding tasks
- research summaries
- transformation tasks
- chunk-level reasoning

This is the default workhorse lane.

### `budget_worker`

Use for:

- extraction
- classification
- deduplication
- chunk summaries
- preprocessing large corpora

Only use it for reversible low-risk work.

### `coder`

Use for:

- code navigation
- candidate patches
- stack trace triage
- unit-test diagnosis

If you do not have a dedicated coder model, map this to your best `fast_worker`.

### `vision_worker`

Use for:

- screenshots
- PDF pages
- dense UIs
- chart or diagram interpretation

### `realtime_worker`

Use for:

- live voice
- streaming assistant turns
- low-latency multimodal sessions

### `media_worker`

Use for:

- image generation and editing
- video generation
- speech synthesis

## Current Example Mapping

Refresh concrete model names before hard-pinning them in production. The examples below are a good default starting point as of April 17, 2026.

| Capability class | OpenAI | Anthropic | Google | Recommended use |
| --- | --- | --- | --- | --- |
| `orchestrator` | `gpt-5.4` | `claude-opus-4.6` | `gemini-3-pro-preview` | planning, final judgment, complex reasoning |
| `reasoner` | `gpt-5.4` | `claude-opus-4.6` or `claude-sonnet-4.6` | `gemini-3-pro-preview` | hard synthesis, architecture, difficult debugging |
| `fast_worker` | `gpt-5.4-mini` | `claude-sonnet-4.6` | `gemini-3-flash-preview` | default delegate for coding, summaries, broad execution |
| `budget_worker` | `gpt-5.4-nano` | `claude-haiku-4.5` | `gemini-2.5-flash-lite` | extraction, tagging, chunk summaries, high-volume low-risk work |
| `vision_worker` | `gpt-5.4-mini` | `claude-sonnet-4.6` | `gemini-3-flash-preview` | screenshots, PDFs, multimodal inspection |
| `realtime_worker` | `gpt-realtime-1.5` or `gpt-realtime-mini` | use general models if no dedicated realtime lane is available | `gemini-3.1-flash-live` or `gemini-2.5-flash-live` | live voice and low-latency interactive sessions |
| `media_worker` | `gpt-image-1.5`, `gpt-image-1-mini` | no direct native media generator in this table | `gemini-3-pro-image-preview`, `gemini-2.5-flash-image`, `Imagen 4`, `Veo 3.1` | image, speech, or video generation |

## Suggested Default Stack

For a lean universal setup, start with only three lanes:

1. `orchestrator`
2. `fast_worker`
3. `budget_worker`

That covers most cost-saving orchestration patterns without overcomplicating routing.

Recommended starting combinations:

- OpenAI-only: `gpt-5.4` + `gpt-5.4-mini` + `gpt-5.4-nano`
- Anthropic-only: `claude-opus-4.6` + `claude-sonnet-4.6` + `claude-haiku-4.5`
- Google-only: `gemini-3-pro-preview` + `gemini-3-flash-preview` + `gemini-2.5-flash-lite`
- Mixed default: `gpt-5.4` as orchestrator, `gpt-5.4-mini` or `claude-sonnet-4.6` as fast worker, `gemini-2.5-flash-lite` or `gpt-5.4-nano` as budget worker

## Role Recommendations by Task

### Repository work

- Orchestrator: define plan, acceptance criteria, final review
- Fast worker: search codebase, summarize modules, draft patches
- Budget worker: batch stack-trace clustering, file tagging, doc extraction

### Research and synthesis

- Budget worker: summarize each source independently
- Fast worker: build comparison matrix
- Orchestrator: produce recommendation and caveats

### Long-document processing

- Budget worker: chunk and extract facts
- Fast worker: consolidate per-section outputs
- Orchestrator: final synthesis or decision

### UI or visual QA

- Vision worker: inspect screenshots and PDFs
- Fast worker: translate observations into actionable issue lists
- Orchestrator: prioritize and decide what matters

## Selection Rules

Prefer:

- `gpt-5.4` when you want one OpenAI model to own the hard reasoning end-to-end
- `gpt-5.4-mini` when you want a strong delegate for coding, documents, and subagent-style work
- `gpt-5.4-nano` when throughput matters more than nuanced reasoning
- `claude-opus-4.6` when the task is heavy on broad reasoning and final judgment
- `claude-sonnet-4.6` as Anthropic's default execution lane
- `claude-haiku-4.5` for lightweight high-volume preprocessing
- `gemini-3-pro-preview` when you want Google's best available multimodal reasoning and coding model
- `gemini-3-flash-preview` when you want Google's best balanced speed-plus-quality worker lane
- `gemini-2.5-flash-lite` for cheapest high-volume multimodal preprocessing

## Refresh Guidance

When updating this file:

1. Check official model overview pages first.
2. Prefer stable model names over previews for production defaults.
3. Keep capability classes stable even when model names change.
4. Record the refresh date whenever concrete mappings change.
