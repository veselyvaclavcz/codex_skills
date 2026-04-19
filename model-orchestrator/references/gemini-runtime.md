# Gemini Runtime

Use this file when you want to keep the whole delegated worker stack inside Google AI Studio and the Gemini API, while Codex stays the top-level orchestrator.

## Recommended Shape

Keep `Codex` as the only orchestrator.

Do not delegate:

- final response composition
- final patch decisions
- risky architectural choices
- user-facing tradeoff calls

Delegate only bounded subtasks to Gemini-family workers.

## Default Lanes

### `gemini-3-flash-preview`

Use as the default external worker when you want the best available balanced Gemini lane.

Best for:

- repository reconnaissance
- file or module summaries
- PDF and screenshot interpretation
- first-pass debugging hypotheses
- transforming notes into tables or JSON
- chunk synthesis that is still non-trivial

This should be the main worker lane in most workflows.

### `gemini-2.5-flash-lite`

Use as the cheapest high-volume lane.

Best for:

- document chunk summaries
- extracting repeated facts
- tagging, classification, deduplication
- log clustering
- converting noisy source material into structured intermediate outputs

Use only for reversible work where a later stronger pass will verify the result.

### `gemini-3-pro-preview`

Use as the escalation and verification lane, not as the default worker.

Best for:

- ambiguous synthesis
- high-context analysis
- difficult debugging
- independent verification of worker outputs
- cases where `flash` produced weak or conflicting candidates

If Codex remains the orchestrator, use `gemini-3-pro-preview` sparingly.

### `gemma-3-27b-it`

Use as an optional alternate lane when you want another model family under the same Google key.

Best for:

- second-opinion text generation
- narrow structured transforms
- prompt variation
- quick low-stakes drafting

Treat it as optional diversity, not as your core reasoning lane.

### Image lane

Use only when the subtask is inherently visual generation or editing.

Primary options:

- `gemini-2.5-flash-image` for conversational image generation and editing
- `gemini-3-pro-image-preview` for stronger image generation when available
- `imagen-4.0-generate-*` variants when the task is pure image generation rather than conversational multimodal work

For image work, route only the visual subtask out. Keep planning and integration in Codex.

### TTS lane

Use only when the workflow explicitly needs speech output.

Options:

- `gemini-2.5-flash-preview-tts` for lower-latency speech
- `gemini-2.5-pro-preview-tts` for higher-quality speech

## Suggested Policy

Use this routing policy first:

1. Codex frames the task and decides if delegation is worth it.
2. `gemini-2.5-flash-lite` handles cheap preprocessing.
3. `gemini-3-flash-preview` handles the main delegated reasoning or summarization task.
4. `gemini-3-pro-preview` is called only if:
   - outputs conflict
   - confidence is low
   - the task turns architectural
   - the stakes become meaningfully higher
5. Image and TTS models are called only for modality-specific subtasks.

This keeps the expensive lane cold unless it is actually needed.

## Role Mapping

Recommended mapping inside this skill:

| Capability class | Model |
| --- | --- |
| `fast_worker` | `gemini-3-flash-preview` |
| `budget_worker` | `gemini-2.5-flash-lite` |
| `reasoner` | `gemini-3-pro-preview` |
| `verifier` | `gemini-3-pro-preview` |
| `alternate_worker` | `gemma-3-27b-it` |
| `media_worker` | `gemini-3-pro-image-preview` or `gemini-2.5-flash-image` |
| `tts_worker` | `gemini-2.5-flash-preview-tts` or `gemini-2.5-pro-preview-tts` |

Codex itself remains the `orchestrator`.

## Example Decompositions

### Codebase task

1. Codex defines the target area and success criteria.
2. `gemini-2.5-flash-lite` tags candidate files or summarizes logs.
3. `gemini-3-flash-preview` summarizes the touched modules and drafts hypotheses.
4. Codex integrates and decides whether any patch plan is sound.
5. `gemini-3-pro-preview` runs only if the evidence is contradictory or the fix is risky.

### Long-document task

1. Codex chunks the material and defines output schema.
2. `gemini-2.5-flash-lite` extracts facts from each chunk.
3. `gemini-3-flash-preview` consolidates topic-level summaries.
4. Codex produces the final synthesis.

### Visual task

1. Codex isolates the visual ask.
2. `gemini-3-pro-image-preview` or `gemini-2.5-flash-image` handles image generation/editing.
3. Codex integrates the result back into the broader workflow.

## Implementation Note

The easiest integration path is to use the Gemini API directly or via its OpenAI-compatible endpoint, then expose a small provider registry in your eventual execution layer.

This skill now includes a ready-to-run script at `scripts/gemini_delegate.py` and a default routing config at `assets/gemini-routing.json`.

Minimal registry shape:

```json
{
  "providers": {
    "google": {
      "api_key_env": "GEMINI_API_KEY"
    }
  },
  "models": {
    "fast_worker": "google/gemini-3-flash-preview",
    "budget_worker": "google/gemini-2.5-flash-lite",
    "reasoner": "google/gemini-3-pro-preview",
    "verifier": "google/gemini-3-pro-preview",
    "alternate_worker": "google/gemma-3-27b-it",
    "media_worker": "google/gemini-3-pro-image-preview"
  }
}
```

Do not bind orchestration logic directly to raw model names in business logic. Keep the model mapping in config.

## Bundled Runtime

Use the bundled runner when you want Codex to actually execute delegated Gemini subtasks:

```powershell
python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" `
  --role fast_worker `
  --prompt "Summarize the touched modules and extract likely failure points."
```

Pipe a long prompt from stdin when that is easier:

```powershell
Get-Content .\delegate-prompt.txt -Raw | python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" --role budget_worker
```

Use attachments for images, PDFs, audio, or local files:

```powershell
python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" `
  --role fast_worker `
  --prompt "Inspect this screenshot and list the top 5 UI defects." `
  --attachment "C:\path\to\screenshot.png"
```

Save generated media outputs:

```powershell
python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" `
  --role media_worker `
  --prompt "Create a clean product hero illustration with a light background." `
  --output-dir "C:\temp\gemini-output"
```

Inspect the resolved payload without calling the API:

```powershell
python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" `
  --role fast_worker `
  --prompt "Test prompt" `
  --dry-run
```

## Runtime Contract

The runner expects:

- `GEMINI_API_KEY` in the environment by default
- role names that exist in `assets/gemini-routing.json`
- prompt text from `--prompt`, `--prompt-file`, or stdin

The runner returns:

- plain text by default
- JSON with `--json`
- saved binary outputs when `--output-dir` is provided and the model returns files

## Practical Recommendation

For the first working version, use only these three lanes:

1. Codex orchestrator
2. `gemini-3-flash-preview`
3. `gemini-2.5-flash-lite`

Add `gemini-3-pro-preview` only as escalation.

After that works reliably, add:

1. `gemma-3-27b-it` as optional alternate text worker
2. `gemini-3-pro-image-preview` or `gemini-2.5-flash-image` as visual lane
