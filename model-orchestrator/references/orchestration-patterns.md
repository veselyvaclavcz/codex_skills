# Orchestration Patterns

Use this file when the task needs a concrete routing pattern, prompt contract, or example decomposition.

## Minimal Delegation Contract

Use this prompt shape for delegated subtasks:

```text
You are handling one bounded subtask inside a larger workflow.

Goal:
Inputs:
Constraints:
Return only:
- Result
- Evidence
- Open questions
- Confidence: high | medium | low

Escalate if:
```

Keep delegate prompts short. If the prompt starts to include project history, summarize first.

## Pattern 1: Split-Merge

Use when many subtasks are independent.

Flow:

1. Orchestrator splits task into parallel units.
2. Fast or budget workers execute each unit.
3. Orchestrator merges and normalizes outputs.
4. Verifier checks the merged result if stakes are non-trivial.

Best for:

- document batches
- file-by-file analysis
- parallel research
- issue clustering

## Pattern 2: Draft-Critique-Revise

Use when first-pass output is cheap but correctness matters.

Flow:

1. Fast worker drafts.
2. Verifier critiques against acceptance criteria.
3. Orchestrator revises or chooses between candidates.

Best for:

- user-facing writing
- code patch proposals
- requirements drafts
- migration plans

## Pattern 3: Chunk-Compress-Solve

Use when source material is too large for the expensive model to read directly.

Flow:

1. Budget worker processes chunks.
2. Fast worker consolidates chunk outputs.
3. Orchestrator solves the real problem from compressed evidence.

Best for:

- long docs
- support logs
- large codebases
- transcript corpora

## Pattern 4: Multi-Candidate Judge

Use when diversity helps.

Flow:

1. Send the same bounded prompt to 2-3 workers.
2. Ask each for a concise output with evidence and confidence.
3. Let the orchestrator compare and choose or synthesize.

Best for:

- architecture options
- bug hypotheses
- naming and API design
- refactor strategies

Do not use this pattern if the judging criteria are still unclear.

## Pattern 5: Specialist Sidecar

Use when one subtask needs a different modality or specialty.

Flow:

1. General model owns the main flow.
2. A specialist model handles one modality-heavy or domain-heavy side task.
3. General model incorporates the result and keeps the thread coherent.

Best for:

- screenshot interpretation
- voice or streaming turns
- image generation
- video generation

## Example: Coding Task

Task: implement a feature across a medium repo while controlling token cost.

Recommended routing:

1. Orchestrator defines scope, affected modules, test expectations.
2. Budget worker tags files and clusters likely touch points.
3. Fast worker summarizes each touched module and drafts candidate edits.
4. Orchestrator decides final patch plan and integrates.
5. Verifier reviews for regressions or missing edge cases.

## Example: Research Task

Task: compare three providers and recommend one.

Recommended routing:

1. Budget worker summarizes each provider independently.
2. Fast worker builds a comparison matrix.
3. Orchestrator writes the recommendation, tradeoffs, and decision rule.

## Example: Large Document Task

Task: synthesize policy changes from a long PDF corpus.

Recommended routing:

1. Budget worker extracts clause-level facts per chunk.
2. Fast worker groups facts by topic and highlights conflicts.
3. Orchestrator writes the final synthesis and unresolved questions.

## Guardrails

Always:

- define output schema before fan-out
- preserve evidence when compressing
- keep a fallback path to a stronger model
- track which outputs are verified versus provisional

Never:

- use cheap workers for final sign-off on high-impact work
- treat long raw context as free
- let each worker invent its own task definition
