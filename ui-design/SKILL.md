---
name: ui-design
description: Improve UI design quality for web and app interfaces. Use when Codex should design, redesign, polish, modernize, restyle, improve layout, hierarchy, density, spacing, typography, color, navigation, forms, dashboards, admin panels, landing pages, chart UI, or design systems. Also use when Codex should choose a visual direction from reference libraries, generate an editable first pass in Figma, support a loop of AI draft to manual visual edits to AI implementation, or translate a manually refined Figma frame back into production code.
---

# UI Design

Use this skill when the problem is visual quality, not just functional correctness.

Default stance:

- preserve the existing design language when one already exists
- prefer editable artifacts over one-shot mockups
- use AI for momentum, not for final visual judgment
- avoid generic filler, weak hierarchy, washed-out gradients, and fake complexity

If the task includes a Figma URL or node ID, also use `figma` or `figma-implement-design`.

## Decide The Lane First

Pick one lane before editing:

- `code-direct`: the system is already strong and the work is mainly polish, density, hierarchy, or implementation
- `figma-first`: direction is weak, several variants are needed, or manual visual refinement will be faster in Figma than in code
- `figma-fidelity`: a specific Figma frame already exists and the main task is faithful implementation

Do not start in code by reflex if the hard part is visual judgment.
Do not start in Figma by reflex if the hard part is straightforward implementation.

## Pick One Mode

Inside the chosen lane, use one mode:

- `project-native`: refine the existing language without importing a new one
- `hybrid-reference`: keep the local system but borrow composition, typography, or token ideas from one strong anchor
- `template-led`: the current UI is weak or generic, so choose one anchor and rebuild toward it

Do not average multiple references together. Choose one primary anchor and at most one narrow secondary reference.

## References

Use references deliberately.

### TypeUI

TypeUI is the main source for visual anchors and page-type direction.

Read in this order:

1. `references/typeui-registry/catalog.md`
2. `references/typeui-registry/page-type-variants.md`
3. only the specific `references/typeui-registry/skills/*.md` files you actually need

### Figma

Figma is the editable iteration surface.

Read:

1. `references/figma-first-workflow.md`
2. `references/figma-prompt-patterns.md`

Use Figma for:

- editable first-pass generation
- structural or stylistic variants
- manual spacing, typography, and rhythm tuning
- comparing alternatives side by side
- locking the chosen frame before implementation

## Workflow

### 1. Ground the task in the real system

Before changing UI, inspect:

- component system and primitives
- typography and color tokens
- spacing density
- target surface such as desktop, mobile, admin, landing page, workflow, or settings
- whether the user wants fidelity, variation, or a stronger reset

For shadcn projects, inspect local `components.json`, global CSS, token definitions, and `components/ui/*` before inventing new patterns.

### 2. State the design thesis

For substantial changes, write one sentence that fixes direction before editing.

Examples:

- `project-native, code-direct: denser CRM review screen with clearer status hierarchy and less chrome`
- `hybrid-reference, figma-first: existing app sharpened with mono-heavy technical typography and stronger left-nav structure`
- `template-led, figma-first: editorial marketing page with restrained serif contrast and large sectional rhythm`

### 3. Use the right medium

Use `code-direct` when:

- the visual language already exists
- the issue is mostly spacing, structure, or component polish
- implementation speed matters more than exploration

Use `figma-first` when:

- the current direction is weak or undefined
- you need a few variants before committing
- the user wants direct visual control
- layout, typography, and rhythm are the hard part

Use `figma-fidelity` when:

- a frame already exists and should be implemented with high fidelity
- the task is handoff, not exploration

### 4. Run the editable loop when needed

If you choose `figma-first`:

1. generate a first pass with Figma AI
2. duplicate the frame before large mutations
3. branch into a small number of meaningful variants
4. use prompts for macro changes
5. use manual edits for spacing, alignment, typography, grouping, and emphasis
6. pick the winning frame
7. hand the exact frame or node back to Codex for implementation

Use AI for macro moves.
Use manual editing for micro moves.

If the issue is a 10-pixel judgment call, stop prompting and edit the frame.

### 5. Implement from primitives

- reuse or extend existing primitives first
- keep component APIs composable and unsurprising
- translate reference logic into local code instead of copying template structure mechanically
- prefer CSS variables, tokens, and shared classes over repeated literals
- if a screen only looks good in the mockup but not in code, the design is not finished

### 6. Validate the interaction layer

Check:

- empty, loading, error, and success states
- hover, focus, active, disabled, and selected states
- label clarity and units
- mobile and desktop behavior
- scanability of tables, forms, and charts

Before finalizing, also read `references/anti-ai-patterns.md` and remove the lazy defaults that make generated UI feel generic.

## Manual Intervention Rule

Manual design edits are first-class, not a fallback.

If the user wants direct visual control:

- keep the work in Figma long enough to settle layout, type, and rhythm
- avoid forcing them to validate small visual choices in code
- capture the chosen result back in code once the frame is stable

## Output Expectations

When the work is substantial:

- say which lane and mode you used
- make the visual direction explicit
- keep hierarchy and interaction coherent across the whole surface
- avoid filler sections and fake complexity
- leave behind editable assets when they help, especially a stable Figma frame or node link
