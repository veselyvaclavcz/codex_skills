# Orchestration Patterns

Use this file when the task needs a concrete split that the user can actually see.

Always start with a delegation ledger, not with implementation.

## Delegation Ledger

Use this exact shape or a close variant:

```text
Delegation Ledger
- Task 1: ...
  Owner: ...
  Why this lane: ...
  Input budget: small | medium | large
  Expected return: ...
- Task 2: ...
  Owner: ...
  Why this lane: ...
  Input budget: small | medium | large
  Expected return: ...
```

If you cannot fill this in clearly, you do not have a good orchestration plan yet.

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

Keep prompts narrow. Shrink context before delegating.

## Pattern 1: Chunk -> Compress -> Judge

Use when large source material would otherwise force the expensive lane to reread too much.

Flow:

1. Split the material into chunks.
2. Budget workers extract facts or summaries per chunk.
3. Fast worker consolidates the chunk outputs.
4. Orchestrator reads only the compressed evidence and decides.

Best for:

- long documents
- logs
- transcripts
- large codebase reconnaissance

## Pattern 2: Scout -> Solve

Use when the main cost is finding the right evidence, not solving once the evidence is known.

Flow:

1. Budget or fast worker scouts candidate files, modules, stack traces, or entities.
2. Orchestrator or fast worker solves using only the narrowed candidate set.

Best for:

- bug localization
- file triage
- dependency impact scans
- issue clustering

## Pattern 3: Fan-Out -> Judge

Use when several units are independent and can run in parallel.

Flow:

1. Split into bounded units.
2. Send each unit to a budget or fast worker.
3. Orchestrator compares only compact returns.
4. Verifier checks the merged result only if risk is non-trivial.

Best for:

- provider-by-provider research
- document batches
- file-by-file analysis
- repeated transforms

## Pattern 4: Draft -> Critique -> Revise

Use when the first draft is cheap but correctness matters.

Flow:

1. Fast worker drafts.
2. Verifier critiques against explicit acceptance criteria.
3. Orchestrator revises or chooses.

Best for:

- patch proposals
- user-facing writing
- migration plans
- refactor options

## Pattern 5: Specialist Sidecar

Use when one subtask needs a different modality.

Flow:

1. General lane owns the thread.
2. A specialist lane handles one modality-heavy subtask.
3. Orchestrator incorporates the result and keeps the workflow coherent.

Best for:

- screenshot interpretation
- PDF reading
- image generation
- speech or media subtasks

## Example: Medium Coding Task

Goal: save expensive-context usage while implementing a feature in a medium repo.

```text
Delegation Ledger
- Task 1: Identify likely touched files
  Owner: budget_worker
  Why this lane: cheap reconnaissance
  Input budget: medium
  Expected return: ranked file list with one-line reasons
- Task 2: Summarize touched modules
  Owner: fast_worker
  Why this lane: broader code understanding on narrowed scope
  Input budget: medium
  Expected return: module summaries and patch candidates
- Task 3: Final patch plan and integration
  Owner: orchestrator
  Why this lane: merge decisions and final judgment
  Input budget: small
  Expected return: accepted implementation plan
```

## Example: Research Task

Goal: compare three vendors without reading full vendor docs in the top lane.

```text
Delegation Ledger
- Task 1: Summarize vendor A
  Owner: budget_worker
- Task 2: Summarize vendor B
  Owner: budget_worker
- Task 3: Summarize vendor C
  Owner: budget_worker
- Task 4: Build comparison matrix
  Owner: fast_worker
- Task 5: Final recommendation
  Owner: orchestrator
```

## Guardrails

Always:

- show the split
- define return schema before fan-out
- compress before merge
- keep verifier optional, not automatic

Never:

- orchestrate without a visible ledger
- delegate tasks that still require the whole thread
- let workers return essays
- pay multi-model cost when one lane would clearly be cheaper
