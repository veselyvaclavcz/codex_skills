# Codex Skills

Three reusable skills for the [OpenAI Codex](https://github.com/openai/codex) coding agent, written
from day-to-day work on real projects. Each skill is a self-contained folder with a `SKILL.md`
(instructions the agent loads on demand), optional scripts and templates.

| Skill | What it solves |
|---|---|
| [`project-context-memory`](project-context-memory/SKILL.md) | Context gets lost between agent threads. The skill keeps a shared project memory on disk (current state, decisions, conversation summaries, an index) so a new thread can pick up where the last one stopped. |
| [`codex-cost-aware-workflow`](codex-cost-aware-workflow/SKILL.md) | Large models are expensive for routine work. The skill sets up a workflow where the main model orchestrates and cheaper subagents handle bounded exploration, small edits, reviews and log summaries, with routing rules written into AGENTS.md. Optionally installs [RTK](https://github.com/rtk-ai/rtk) to cut tool-output tokens. |
| [`ui-design`](ui-design/SKILL.md) | AI-generated UI tends to look generic. The skill gives the agent a design review checklist, anti-pattern list, surface playbooks (dashboards, forms, landing pages) and a library of 57 visual style references to pick a deliberate direction. |

## Install

Copy a skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\project-context-memory "$env:USERPROFILE\.codex\skills\"
```

On macOS/Linux use `~/.codex/skills/`.

## Example: shared project memory

```powershell
# in your project folder: create the memory structure once
python "$env:USERPROFILE\.codex\skills\project-context-memory\scripts\bootstrap_project_memory.py" --root .

# at the start of a thread: load the current state
python "$env:USERPROFILE\.codex\skills\project-context-memory\scripts\sync_project_memory.py" --mode start
```

After that, ask Codex as usual, e.g. *"continue with the open items from the last session"*;
the skill tells it to read and update the memory files instead of relying on chat history.

## Example: cost-aware workflow

```powershell
python "$env:USERPROFILE\.codex\skills\codex-cost-aware-workflow\scripts\setup_cost_aware_workflow.py" --root . --scope project --smoke-test
```

This writes the subagent definitions and an AGENTS.md routing block into the project and
runs a quick check that everything is wired up.

## Third-party content

`ui-design/references/typeui-registry/` contains style files from
[bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills)
(TypeUI registry), used under the MIT license. See [THIRD_PARTY.md](THIRD_PARTY.md).

## License

MIT for the original content of this repository, see [LICENSE](LICENSE).
Third-party content keeps its own license, see [THIRD_PARTY.md](THIRD_PARTY.md).
