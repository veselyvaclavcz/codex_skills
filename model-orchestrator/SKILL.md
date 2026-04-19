---
name: model-orchestrator
description: Universal multi-model orchestration for cost-aware task routing, delegation, fallback selection, and specialist model usage across providers. Use when Codex needs to split work into subtasks, offload narrow or repetitive work to cheaper/faster models, choose specialized models for coding/vision/audio/media tasks, design provider-agnostic model registries, or build layered AI workflows that balance quality, latency, and token spend.
---

# Model Orchestrator

Use this skill to run a layered model stack instead of forcing one model to do every step. Keep planning, integration, and final judgment in a stronger model; push narrow, repeatable, or modality-specific work to cheaper or more specialized models.

For the simplest production shape, start with a Gemini-only worker stack and keep Codex as the orchestrator.

This skill includes an executable Gemini runner and a ready-to-use routing config so it can actually delegate work, not just describe delegation.

## Core Rule

Optimize for total workflow cost and reliability, not for the IQ of a single call.

That usually means:

1. Keep decomposition, acceptance criteria, and final sign-off in the strongest available model.
2. Delegate bounded subtasks to the cheapest model that can do them reliably.
3. Escalate back up when uncertainty, ambiguity, or impact increases.

## Workflow

### 1. Normalize the Work

Split the request into work units and tag each unit with:

- `task_type`: planning, search, extraction, summarization, coding, review, transformation, critique, vision, audio, media generation
- `risk`: low, medium, high
- `reversibility`: easy or expensive to undo
- `latency_sensitivity`: low or high
- `context_size`: small, medium, large
- `requires_tools`: yes or no
- `needs_final_judgment`: yes or no

If the task is still fuzzy, do not delegate yet. Clarify the task locally first.

### 2. Route by Capability Class

Use stable capability classes instead of hard-coding vendor assumptions:

- `orchestrator`: top-level planning, decomposition, acceptance criteria, final judgment
- `reasoner`: hard synthesis, ambiguous reasoning, architecture, tradeoff analysis
- `fast_worker`: broad low-to-medium risk execution with good speed/cost balance
- `budget_worker`: high-volume classification, extraction, chunk summaries, first-pass transforms
- `coder`: patch drafting, test triage, code navigation, targeted refactors
- `vision_worker`: screenshots, PDFs, dense UI, image-heavy inputs
- `realtime_worker`: live voice or interactive streaming
- `media_worker`: image, video, or speech generation
- `verifier`: independent critique, validation, or cross-check

For concrete current examples, read [references/model-registry.md](references/model-registry.md).
For a Gemini-only deployment, read [references/gemini-runtime.md](references/gemini-runtime.md).

### 3. Decide What Not to Delegate

Keep work local when any of the following is true:

- Requirements are ambiguous.
- A subtask depends on most of the full conversation or codebase context.
- The action is high-risk, externally visible, or hard to reverse.
- The real value is in integration and judgment rather than raw generation.
- The user expects one coherent reasoning chain rather than many partial outputs.

Good delegation targets:

- batch classification
- fact extraction from many documents
- chunk summaries
- log triage
- file-by-file code reconnaissance
- candidate patch drafting
- rewrite variants
- first-pass review comments
- modality-specific processing such as screenshots or audio

### 4. Shrink Context Before Delegation

Never forward the whole conversation by default.

Pass only:

- the concrete goal
- the minimum source artifacts
- constraints
- the required output schema
- acceptance criteria

If a subtask needs too much context, compress first:

- summarize the repo area
- extract only relevant files
- chunk long documents
- replace prose with tables or bullet facts
- provide explicit unknowns instead of full history

### 5. Use a Delegation Contract

Every delegate should receive a narrow contract like this:

```text
Goal:
Inputs:
Constraints:
Return only:
Evidence required:
Confidence:
Escalate if:
```

Preferred return shape:

```text
Result:
Evidence:
Open questions:
Confidence: high | medium | low
```

Do not ask delegates to re-plan the entire project unless that is the subtask.

When executing a real delegated task through this skill, call:

```powershell
python "C:\Users\mail\Desktop\Claude Expert Projects\Projects\skills\model-orchestrator\scripts\gemini_delegate.py" --role fast_worker --prompt "..."
```

Use `assets/gemini-routing.json` as the default role-to-model map unless the workspace provides a more specific override.

### 6. Verify and Merge

Use the stronger model to:

- compare outputs from multiple workers
- reject low-confidence or weakly evidenced results
- merge partial outputs
- make final tradeoff calls
- prepare the final user-facing answer or final code change

For high-impact tasks, use a separate `verifier` lane instead of trusting the generating worker.

## Routing Heuristics

Use these defaults unless task evidence suggests otherwise:

- `orchestrator` for planning, decomposition, and final synthesis
- `reasoner` for architecture, debugging deadlocks, conflict resolution, and hard edge cases
- `fast_worker` for most delegated coding, research, summarization, or transformation work
- `budget_worker` for batch extraction, tagging, deduplication, chunk summaries, and document preprocessing
- `coder` for patch candidates, stack trace triage, test failure clustering, and file-level analysis
- `vision_worker` for screenshots, OCR-like interpretation, complex diagrams, and dense UI review
- `media_worker` only when the task is inherently image, video, or speech generation

If two classes seem viable, prefer the cheaper one first and add a verification step.

## Fallback and Escalation

Escalate to a stronger model when:

- confidence is low
- outputs conflict
- schema adherence fails twice
- a worker invents facts or code context
- important constraints were missed
- the task becomes architectural rather than local
- the action has security, legal, financial, or production impact

Fallback order should usually move:

1. `budget_worker` -> `fast_worker`
2. `fast_worker` -> `reasoner`
3. `reasoner` -> `orchestrator`

Do not escalate everything to the top model by reflex. Escalation exists to protect correctness, not to avoid thinking about routing.

## Provider Abstraction

Keep provider choice separate from routing logic.

Represent each model with normalized metadata such as:

- `id`
- `provider`
- `capability_class`
- `modalities`
- `tool_support`
- `context_window`
- `latency_tier`
- `cost_tier`
- `strengths`
- `weaknesses`
- `default_use_cases`
- `fallback_to`

This lets the same orchestration policy work with hosted APIs, local models, or future providers.

Use this skill with any of these execution layers:

- native subagents exposed by the current environment
- MCP tools that proxy external providers
- local or self-hosted model runners
- custom CLI wrappers around vendor APIs
- OpenCode as a runtime and provider router

### OpenCode Runtime

Use OpenCode when you want a real execution backend for delegated agents instead of a purely conceptual routing plan.

OpenCode is a good fit when you need:

- per-agent model overrides
- a shared project runtime for multiple agent roles
- direct provider configuration in `opencode.json`
- a cheap fallback lane without rewriting your orchestration policy

For a Gemini-first setup:

1. Use direct Gemini models as the primary `orchestrator`, `reasoner`, or `fast_worker` lanes.
2. Use OpenCode Go only as an optional fallback for cheap open-model workers.
3. Keep model routing bound to capability class, then map each class to an OpenCode model ID.

Do not treat OpenCode Go as a Gemini substitute. It is a curated open-model subscription, not a Gemini pass-through.

### Gemini-First Runtime

If you want the lowest-friction setup, keep the whole delegated worker layer inside Google AI Studio and Gemini API.

Recommended default:

1. Keep Codex as `orchestrator`.
2. Use `gemini-3-flash-preview` as the default external worker.
3. Use `gemini-2.5-flash-lite` for cheap preprocessing and high-volume reversible work.
4. Use `gemini-3-pro-preview` only for escalations, hard synthesis, and independent verification.
5. Use `gemini-3-pro-image-preview` or `gemini-2.5-flash-image` only for image generation or editing tasks.

This gives you multiple lanes under one Google API key without introducing another provider yet.

## Default Patterns

### Scout -> Solve -> Verify

Use a cheap worker to gather evidence, a stronger worker to solve, and an independent worker to verify.

### Fan-Out -> Judge

Send the same bounded prompt to multiple low-cost workers, then let one stronger model compare and select.

### Chunk -> Compress -> Synthesize

Use budget workers to process large corpora, then hand only compressed outputs to the reasoner.

### Draft -> Critique -> Revise

Use a fast worker for first draft, a verifier for critique, and the orchestrator for final revision.

## Anti-Patterns

Avoid these failure modes:

- delegating tasks before the task is well framed
- sending giant contexts to cheap models and expecting savings
- asking low-cost workers for final policy or architecture decisions
- mixing planning and execution inside every worker prompt
- trusting a specialist model outside its specialty
- failing to define acceptance criteria before fan-out

## References

- Read [references/model-registry.md](references/model-registry.md) for a provider-agnostic registry schema and a current example mapping of concrete models to roles.
- Read [references/orchestration-patterns.md](references/orchestration-patterns.md) for reusable prompt contracts, routing templates, and example task decompositions.
- Read [references/gemini-runtime.md](references/gemini-runtime.md) for a Gemini-only stack with Codex as orchestrator and Gemini models as delegated workers.
- Read [references/opencode-runtime.md](references/opencode-runtime.md) for a concrete OpenCode setup with Gemini as the primary stack and OpenCode Go as an optional low-cost fallback lane.
- Use [scripts/gemini_delegate.py](scripts/gemini_delegate.py) to execute delegated Gemini subtasks through the default routing config at [assets/gemini-routing.json](assets/gemini-routing.json).
