---
name: project-context-memory
description: Bootstrap and maintain shared project memory on disk so multiple Codex threads can work on the same project without losing context. Use by default for substantial coding, debugging, planning, documentation, or project organization work inside a project workspace when continuity across threads matters. Also use when Codex should initialize project documentation in an empty or undocumented workspace, create a standard memory folder structure, record conversation summaries, update decisions and current state, or rebuild a conversation index that later threads can read.
---

# Project Context Memory

Use this skill to keep project context on disk instead of trapped inside one thread.

The core idea is simple:

1. Create a shared memory folder inside the project.
2. Read it at the start of new threads.
3. Update it whenever a meaningful decision, summary, or task outcome happens.

When this skill is active, prefer automatic memory maintenance over waiting for the user to ask.

This skill also maintains a managed block inside the project `AGENTS.md` so future threads are nudged to use both shared memory and the cost-aware workflow consistently.

## Default Layout

This skill uses `docs/project-memory/` inside the project root.

Bootstrap creates:

- `docs/project-memory/README.md`
- `docs/project-memory/project-summary.md`
- `docs/project-memory/current-state.md`
- `docs/project-memory/decisions.md`
- `docs/project-memory/open-questions.md`
- `docs/project-memory/conventions.md`
- `docs/project-memory/conversations/index.md`
- `docs/project-memory/conversations/YYYY/`
- `AGENTS.md` if missing, or a managed project-memory block inside an existing `AGENTS.md`

Use this layout unless the repo already has a stronger documentation convention.

For `AGENTS.md`, the rule is:

- never delete user-authored content outside the managed block
- keep the managed block updated on every sync
- use the managed block to push consistent use of `$project-context-memory` and conditional use of `$codex-cost-aware-workflow`

## Workflow

### 1. Bootstrap If Missing

At the start of work, immediately run the autopilot sync wrapper:

```powershell
python "C:\Users\mail\.codex\skills\project-context-memory\scripts\sync_project_memory.py" --mode start
```

This wrapper:

- detects the project root from the current directory
- bootstraps `docs/project-memory/` if missing
- creates or updates the managed `AGENTS.md` block
- prints the memory root and high-signal files to read

Do this proactively when the skill triggers. Do not wait for a separate user instruction.

At the start of work, check whether `docs/project-memory/` exists.

If it does not exist, run:

```powershell
python "C:\Users\mail\.codex\skills\project-context-memory\scripts\bootstrap_project_memory.py" --root "C:\path\to\project"
```

If the workspace is almost empty, still bootstrap it. The point is to create a stable place for future threads to write and read context.

### 2. Read Shared Context First

Before making plans in a new thread, read:

- `README.md`
- `project-summary.md`
- `current-state.md`
- `decisions.md`
- `open-questions.md`
- relevant recent files from `conversations/`

Do not assume the previous thread exists in memory. Treat the on-disk project memory as the authoritative shared context.

### 3. Record Meaningful Milestones

Create a conversation note when:

- a task plan becomes concrete
- a decision is made
- a bug investigation reaches a useful conclusion
- a feature branch or implementation milestone lands
- the thread ends with useful unresolved context

Use:

```powershell
python "C:\Users\mail\.codex\skills\project-context-memory\scripts\record_conversation.py" `
  --root "C:\path\to\project" `
  --title "Fix login redirect regression" `
  --summary "Investigated redirect loop and narrowed the issue to callback URL normalization." `
  --decision "Keep the callback normalization in middleware, not in the controller." `
  --next-step "Patch the middleware and add one regression test."
```

Repeat `--decision`, `--file`, `--next-step`, and `--tag` as needed.

For lower-friction operation, prefer the wrapper:

```powershell
python "C:\Users\mail\.codex\skills\project-context-memory\scripts\sync_project_memory.py" `
  --mode checkpoint `
  --title "Fix login redirect regression" `
  --summary "Investigated redirect loop and narrowed the issue to callback URL normalization." `
  --decision "Keep the callback normalization in middleware, not in the controller." `
  --next-step "Patch the middleware and add one regression test."
```

Use `--mode finish` at the end of a thread when you want a durable closing note with next steps for later threads.

### 4. Keep High-Signal Files Updated

Use conversation notes for thread-local history.

Use the top-level memory files for durable shared state:

- `project-summary.md`: what the project is and what matters
- `current-state.md`: current implementation and work in progress
- `decisions.md`: durable technical and product decisions
- `open-questions.md`: unresolved issues worth revisiting
- `conventions.md`: repo-specific rules and working norms

Conversation notes should not become the only source of truth.

### 5. Rebuild the Conversation Index

If notes are added manually or imported from elsewhere, rebuild the index:

```powershell
python "C:\Users\mail\.codex\skills\project-context-memory\scripts\rebuild_conversation_index.py" --root "C:\path\to\project"
```

## Recommended Behavior In Threads

When this skill is active:

1. Run the sync wrapper in `start` mode immediately.
2. Read existing memory before proposing a plan.
3. Update memory after important milestones without waiting for a reminder.
4. Run the sync wrapper in `finish` mode before leaving a thread with meaningful state.
5. Leave the project in a state that a fresh thread can resume.

## What This Skill Does Not Do

It does not magically share hidden thread history between Codex threads.

It makes shared memory explicit by writing it to project files.

## Resources

- Use [scripts/bootstrap_project_memory.py](scripts/bootstrap_project_memory.py) to create the folder structure and starter files.
- Use [scripts/record_conversation.py](scripts/record_conversation.py) to create conversation notes and update the index.
- Use [scripts/rebuild_conversation_index.py](scripts/rebuild_conversation_index.py) to regenerate the conversation index from note files.
- Use [scripts/sync_project_memory.py](scripts/sync_project_memory.py) as the default low-friction entry point for automatic bootstrap and checkpoint logging.
- Read [references/layout.md](references/layout.md) for the file structure and note semantics.
