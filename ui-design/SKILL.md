---
name: "ui-design"
description: "Improve UI design quality for web and app interfaces. Use when the task is to design, redesign, polish, modernize, restyle, improve layout, hierarchy, density, spacing, typography, colors, navigation, forms, dashboards, admin panels, landing pages, chart UI, or design systems. Also use when Codex should choose a visual direction from reference libraries, generate an editable first pass in Figma, support a loop of AI draft -> manual visual edits -> AI implementation, or translate a manually refined Figma frame back into production code."
---

# UI Design

Use this skill when the task is about making an interface look and feel better, not just making it function.

This skill is Figma-first, not prompt-only.

Preferred workflow:

1. choose a visual direction
2. generate an editable first pass in Figma
3. manually refine details in Figma
4. hand the chosen frame back to Codex for implementation

If the task includes a Figma URL or node ID, also use `figma` or `figma-implement-design`. Figma remains the source of truth for exact implementation.

## Core Rules

- Preserve the existing design system when one already exists.
- Prefer editable design artifacts over one-shot HTML mockups.
- Use AI to create momentum, not to replace visual judgment.
- Let the user intervene directly in Figma whenever prompt iteration becomes noisy.
- Pick one visual direction per screen and carry it through consistently.
- Do not ship obvious AI filler: weak hierarchy, generic stat cards, washed-out gradients, decorative copy, or empty visual complexity.
- Favor reusable primitives and tokenized styling over scattered literals and throwaway wrappers.

## Execution Lanes

Choose one lane up front:

- `Code-direct`: the repo already has a strong system and the work is mostly implementation, polish, hierarchy, or density.
- `Figma-first`: direction is unclear, several variants are needed, or visual refinement will be faster in a design editor than in code.
- `Figma-fidelity`: a specific Figma frame already exists and the main task is faithful implementation.

Do not start in code by reflex if the hard part is visual judgment. Do not start in Figma by reflex if the visual system is already settled.

## Working Modes

Inside the chosen lane, pick one mode:

- `Project-native`: refine the existing language without importing a new one.
- `Hybrid reference`: keep the local system, but borrow composition, typography, or token ideas from one strong anchor.
- `Template-led`: the current UI is weak or generic, so choose one anchor and rebuild toward it.

Do not average multiple anchors together. Choose one primary anchor and at most one narrow secondary reference.

## Reference Sources

Use references deliberately instead of mixing everything at once.

### TypeUI

TypeUI is the stable source for visual anchors and page-type direction.

Read in this order:

1. `references/typeui-registry/catalog.md`
2. `references/typeui-registry/page-type-variants.md`
3. only the specific `references/typeui-registry/skills/*.md` files you need

### Figma AI and handoff

Figma is the editable iteration surface.

Use it for:

- editable first-pass generation
- structural or stylistic variants
- manual spacing, typography, and rhythm tuning
- comparing alternatives side by side
- locking the chosen frame before implementation

Read:

1. `references/figma-first-workflow.md`
2. `references/figma-prompt-patterns.md`

## Workflow

### 1. Ground the task in real constraints

Before changing UI, inspect:

- component system and primitives
- typography and color tokens
- spacing density
- target surface: desktop, mobile, admin, landing page, workflow, settings
- whether the user wants fidelity, variation, or a stronger reset

For shadcn projects, inspect local `components.json`, global CSS, token definitions, and `components/ui/*` before inventing patterns.

### 2. State the design thesis

When the change is substantial, write one sentence that fixes the direction before editing.

Examples:

- `Project-native, code-direct: denser CRM review screen with clearer status hierarchy and less chrome.`
- `Hybrid, Figma-first: existing app sharpened with mono-heavy technical typography and stronger left-nav structure.`
- `Template-led, Figma-first: editorial marketing page with restrained serif contrast and large sectional rhythm.`

### 3. Choose the right medium

Use `Code-direct` when:

- the visual language already exists
- the issue is mostly spacing, structure, or component polish
- implementation speed matters more than visual exploration

Use `Figma-first` when:

- the current design direction is weak or undefined
- you need 2-4 variants before committing
- the user wants to manually adjust the result
- layout, typography, and rhythm are the hard part

Use `Figma-fidelity` when:

- a frame already exists and should be implemented with high fidelity
- the task is mainly handoff, not exploration

### 4. Run the editable Figma loop

If you choose `Figma-first`:

1. Generate a first pass with Figma AI using First Draft or Figma Make.
2. Duplicate the frame before big mutations.
3. Branch into a small number of meaningful variants.
4. Use prompts for structural or thematic changes.
5. Use direct manual edits for spacing, typography, alignment, grouping, and emphasis.
6. Pick the winning frame.
7. Hand the exact frame or node URL back to Codex for implementation through Figma MCP.

The Figma frame is the working surface. The codebase is the durable product output.

### 5. Use AI for macro moves, manual edits for micro moves

Good AI tasks:

- first-pass layout generation
- alternate navigation structures
- light or dark theme shifts
- tone or aesthetic pivots
- adding or removing sections

Good manual tasks:

- spacing rhythm
- font swaps
- weight and size tuning
- edge alignment
- visual emphasis and scan order
- section compression

If the issue is a 10-pixel judgment call, stop prompting and edit the frame.

### 6. Implement from primitives

- Reuse or extend existing primitives first.
- Keep component APIs composable and unsurprising.
- Translate reference logic into local code rather than copying template structure mechanically.
- Prefer CSS variables, tokens, and shared classes over repeated literals.
- If a screen only looks good in the mockup but not in code, the design is not finished.

### 7. Validate the interaction layer

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

Use AI for exploration. Use manual editing for judgment-heavy refinement.

## References

Read these files as needed:

- `references/figma-first-workflow.md`: editable Figma-first loop from AI draft to manual refinement to MCP handoff
- `references/figma-prompt-patterns.md`: practical Figma AI mutation patterns and prompt shapes
- `references/typeui-registry/catalog.md`: index of TypeUI anchors
- `references/typeui-registry/page-type-variants.md`: page-type to anchor mapping
- `references/typeui-registry/skills/*.md`: deep anchor guidance
- `references/surface-playbooks.md`: screen-type guidance
- `references/shadcn-principles.md`: shadcn-friendly theming and component rules
- `references/anti-ai-patterns.md`: generic UI failure modes to remove

## Output Expectations

When you implement UI changes:

- say which lane and mode you used when the work is substantial
- make the visual direction explicit
- keep hierarchy and interaction coherent across the whole surface
- avoid meaningless filler sections and fake complexity
- leave behind editable assets when they help, especially a stable Figma frame or node link
