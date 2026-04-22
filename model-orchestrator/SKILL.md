---
name: model-orchestrator
description: "Universal multi-model orchestration for cost-aware task routing, visible subtask delegation, fallback selection, and specialist model usage across providers. Use when Codex should explicitly split work into bounded subtasks, delegate some of them to cheaper or more specialized models, and make that delegation legible to the user instead of silently doing all reasoning in one expensive lane."
---

# Model Orchestrator

Use this skill only when orchestration is real.

If the task will not be split into visible subtasks with at least one delegated away from the main reasoning lane, do not use this skill. Just solve the task normally.

This skill exists to lower total cost and context load, not to add fake ceremony.

## Core Rule

The user should be able to point at:

- the subtasks
- which lane owns each subtask
- why a cheaper lane is safe there
- what stayed with the orchestrator

If that is not visible, the orchestration failed even if the answer is correct.

## Activation Gate

Use this skill only when all of these are true:

1. The work can be split into at least `2` bounded subtasks.
2. At least `1` subtask can go to a cheaper or narrower lane than the orchestrator.
3. The delegated subtasks do not need the whole conversation or codebase.
4. Delegation reduces expensive-context reading, not just moves the same prompt elsewhere.

If any of these fail, do not orchestrate.

## Token-Savings Test

Before delegating, run a quick sanity check.

Delegate only when most of these are true:

- the delegated prompt is much smaller than the full context
- the subtask is repetitive, chunkable, or reversible
- the cheap lane can return compressed evidence instead of raw material
- the orchestrator would otherwise reread large low-signal context

Do not delegate when:

- every worker needs the same giant context
- the expensive part is integration and judgment, not generation
- the subtask is high-risk and hard to undo
- you are only adding an extra model hop without shrinking context

## Required Workflow

### 1. Build a visible delegation ledger

Before running workers, write a compact ledger in this shape:

```text
Delegation Ledger
- Task 1: ...
  Owner: orchestrator | budget_worker | fast_worker | reasoner | verifier | specialist
  Why this lane: ...
  Input budget: small | medium | large
  Expected return: ...
- Task 2: ...
```

The user should see this before or while the work runs.

### 2. Keep the orchestrator thin

The orchestrator should do only:

- decomposition
- acceptance criteria
- routing
- merge decisions
- final sign-off

Do not let the orchestrator also do all the heavy lifting while pretending to delegate.

### 3. Delegate only bounded work

Good delegation targets:

- batch classification
- chunk summaries
- file-by-file reconnaissance
- log clustering
- first-pass extraction
- candidate patch drafting
- screenshot or PDF interpretation

Bad delegation targets:

- fuzzy requirements
- high-stakes final judgment
- tasks that need most of the whole repo or thread
- tasks where the cheap lane will just hallucinate missing context

### 4. Use a hard prompt contract

Every delegate should receive:

```text
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

Never send raw thread history by default.

### 5. Merge compressed evidence, not verbose prose

Workers should return:

- short factual findings
- narrow diffs or recommendations
- unresolved uncertainties

They should not return essays. Long worker outputs erase token savings.

### 6. Verify only where needed

Use a verifier lane when:

- the task is externally visible
- two workers disagree
- the patch or recommendation is risky
- a cheap lane handled noisy evidence

Do not add verifier cost to trivial reversible work.

## Routing Lanes

Use stable capability classes:

- `orchestrator`: decomposition, routing, merge, final judgment
- `budget_worker`: cheap extraction, chunk summaries, tagging, clustering
- `fast_worker`: broad low-to-medium-risk execution
- `reasoner`: hard synthesis, architecture, contradictory evidence
- `coder`: patch candidates, file-level code analysis, test triage
- `vision_worker`: screenshots, PDFs, dense UI, image-heavy inputs
- `media_worker`: image, speech, or video generation
- `verifier`: independent critique or regression check

Prefer the cheapest lane that can do the subtask reliably.

## Patterns That Actually Save Tokens

### Chunk -> Compress -> Judge

Use when the source is large.

1. Budget workers process chunks independently.
2. Fast worker consolidates chunk outputs.
3. Orchestrator reads only compressed evidence and makes the decision.

### Scout -> Solve

Use when the expensive part is finding relevant evidence.

1. Budget or fast worker scouts likely files, issues, or regions.
2. Orchestrator or fast worker solves only on the narrowed set.

### Fan-Out -> Judge

Use when multiple independent units can run in parallel.

1. Split into bounded units.
2. Send each unit to a cheap lane.
3. Orchestrator compares only the compact returns.

### Draft -> Critique -> Revise

Use when first draft is cheap but correctness matters.

1. Fast worker drafts.
2. Verifier critiques.
3. Orchestrator revises or selects.

## Anti-Patterns

Treat these as failures:

- saying "I'll orchestrate" and then doing everything in one lane
- delegating without showing the subtask split
- delegating tasks that still carry giant shared context
- using cheap workers for final architectural or policy decisions
- letting workers return long prose blobs
- paying verifier cost on trivial reversible tasks
- fan-out without fixed output schema

## Execution Guidance

When you actually run delegated Gemini tasks through this skill:

- use [scripts/gemini_delegate.py](scripts/gemini_delegate.py)
- use [assets/gemini-routing.json](assets/gemini-routing.json) unless the workspace overrides it
- prefer `--json` when you want structured downstream merge
- use `--dry-run` first if the prompt or lane choice still looks suspicious

Example:

```powershell
python "C:\Users\mail\Desktop\Projekty\codex_skills\model-orchestrator\scripts\gemini_delegate.py" `
  --role budget_worker `
  --prompt-file .\subtask-01.txt `
  --json
```

## References

- Read [references/orchestration-patterns.md](references/orchestration-patterns.md) for concrete visible-ledger patterns and example decompositions.
- Read [references/token-savings-checklist.md](references/token-savings-checklist.md) before delegating if it is unclear whether orchestration actually saves anything.
- Read [references/model-registry.md](references/model-registry.md) for a provider-agnostic mapping of concrete models to lanes.
- Read [references/gemini-runtime.md](references/gemini-runtime.md) for a Gemini-only delegated worker stack.
- Read [references/opencode-runtime.md](references/opencode-runtime.md) for an OpenCode-based runtime option.
