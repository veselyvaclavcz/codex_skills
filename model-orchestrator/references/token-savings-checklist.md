# Token Savings Checklist

Use this file when it is unclear whether orchestration will actually reduce cost.

## Quick decision

If the answer to most of these is `no`, do not orchestrate.

- Can the task be split into at least two bounded subtasks?
- Can at least one subtask run on a cheaper lane?
- Can each delegated prompt be much smaller than the full context?
- Will workers return compressed evidence instead of long prose?
- Will the orchestrator avoid rereading the raw source material?

## Good signs

- the task is chunkable
- the task contains repeated low-risk operations
- evidence can be summarized before merge
- independent units can run in parallel
- the expensive lane only needs the compressed result

## Bad signs

- every worker still needs the whole repo or thread
- the expensive part is final judgment, not evidence gathering
- output quality depends on one coherent full-context chain
- worker outputs will be long and hard to compare
- there is no obvious cheaper lane that is safe

## Cheap-lane sweet spots

Use budget or fast workers for:

- extraction
- classification
- chunk summaries
- file triage
- log clustering
- first-pass transforms

Keep these with the orchestrator or reasoner:

- final architecture choice
- risky code integration
- externally visible high-stakes decisions
- contradictory evidence resolution

## Practical heuristic

Orchestration is usually worth it when:

- the delegated input can be reduced to less than half of the full context
- the worker return can be reduced to a few bullets, a matrix, or a ranked list
- the top lane can make the final call from compressed evidence

Orchestration is usually not worth it when:

- you are just moving the same big prompt to another model
- you cannot explain the savings in one sentence

## One-sentence test

Before delegating, force yourself to say:

`This saves tokens because ...`

If the sentence is weak, the orchestration plan is weak.
