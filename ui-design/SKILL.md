---
name: "ui-design"
description: "Improve UI design quality for web and app interfaces. Use when the task is to design, redesign, polish, modernize, restyle, make more compact, improve layout, hierarchy, UX, spacing, typography, colors, visual style, alignment, density, readability, dashboards, landing pages, forms, settings, admin panels, chart UI, or design systems. Supports project-native refinement, hybrid work that borrows from a local design-template library, and template-led exploration when a stronger visual direction is needed. Also trigger for requests like make it look better, improve the UI, improve the frontend, fix the layout, make it feel premium, avoid AI slop, or Czech prompts such as zlepsi UI, vylepsi design, uprav layout, dolad barevnost, udelej to kompaktnejsi, moderni, prehlednejsi, pouzitelnejsi."
---

# UI Design

Use this skill when the task is about making an interface look and feel better, not just making it function.

If the task includes a Figma URL or node ID, also use `figma` or `figma-implement-design`. Figma remains the source of truth for exact implementation; this skill improves design judgment and UI quality.

## Core Rules

- Preserve the existing design system when one already exists.
- Decide explicitly whether the work is project-native, hybrid, or template-led before editing.
- Use the local TypeUI library as a reference database, not as a mandatory source.
- If the current UI is weak or generic, pick one clear visual direction and carry it through consistently.
- Do not produce "AI slop": avoid default-centered cards, oversized spacing, washed-out gradients, interchangeable SaaS layouts, and decorative filler copy.
- Favor open, editable code and reusable primitives over opaque one-off hacks.
- Design for the dominant use case first: dashboard, marketing page, workflow screen, settings, mobile control surface, and so on.

## Working Modes

Choose one mode up front:

- `Project-native`: the repo already has a coherent system; refine hierarchy, density, copy, layout, and interaction without importing a new visual language.
- `Hybrid reference`: the repo has some direction, but needs help; use the local TypeUI library to borrow composition, typography, or token ideas while still adapting to the project.
- `Template-led`: the project lacks a credible visual direction or the user wants variants; choose one reference style as the anchor and use it as a strong blueprint.

Do not mix multiple modes in one screen. If you borrow from the library, choose one anchor reference and at most one secondary reference for a narrow concern such as typography or navigation.

## Workflow

### 1. Ground the task in real constraints

Before changing UI, inspect:

- the existing component system
- typography and color tokens
- spacing density
- target surface: desktop, mobile, admin, landing page, form, chart-heavy app
- whether the user wants fidelity to an existing pattern or a stronger redesign

For shadcn-based projects, inspect local `components.json`, global CSS, token definitions, and `components/ui/*` before inventing new patterns.

### 2. Decide the source of direction

Make one explicit choice:

- stay native to the repo
- stay native, but consult the reference library
- use the reference library as the main design anchor

When using the library:

1. read `references/typeui-registry/catalog.md`
2. read `references/typeui-registry/page-type-variants.md`
3. open only the specific template files you need from `references/typeui-registry/skills/*.md`

If the reference library conflicts with the product's existing system, adapt the reference. Do not blindly transplant it.

### 3. Set a design thesis

When the work is substantial, state a short design thesis before editing. Include mode and anchor source. Example:

- "Project-native refinement: compact trading-style dashboard with tight spacing, strong data hierarchy, and subdued chrome."
- "Hybrid reference: existing shadcn system sharpened with mono-heavy, technical hierarchy from the TypeUI `mono` template."
- "Template-led: editorial landing page anchored in TypeUI `editorial`, adapted to the product palette and content."

Make the code reflect that thesis.

### 4. Build from primitives, not from decoration

- Reuse or extend existing primitives first.
- Keep component APIs predictable and composable.
- Prefer tokenized colors, spacing, radii, and typography over scattered literals.
- If a component almost fits, edit the open code directly instead of wrapping it into a mess.
- When borrowing from a template, translate the visual logic into local primitives instead of copying the entire structure mechanically.

### 5. Make hierarchy obvious

Every screen should quickly answer:

- what is primary
- what is secondary
- what is actionable
- what is status or context

Use size, weight, contrast, spacing, and alignment intentionally. Do not rely on borders everywhere.

### 6. Match density to task

- Dashboards and internal tools should usually be denser and more information-rich.
- Marketing and onboarding can breathe more, but still need rhythm and focus.
- Forms should minimize ambiguity and keep the next action obvious.
- Mobile and small surfaces need stronger prioritization and progressive disclosure.

### 7. Run the anti-pattern filter

Before finalizing, read `references/anti-ai-patterns.md` and remove the lazy default moves that make AI-generated UI feel generic. Treat it as a pressure test, not as a ban on all personality.

### 8. Validate the interaction layer

Check:

- empty, loading, error, and success states
- hover, focus, active, disabled, and selected states
- label clarity and units
- chart labels and time ranges
- keyboard and screen-reader basics when applicable
- desktop and mobile behavior

## Template Library Usage

The bundled TypeUI library is a local database of complete style templates.

Use it in two ways:

- `Reference mode`: inspect several variants for inspiration, then adapt the ideas to the local system.
- `Anchor mode`: choose one template as the dominant visual language when the project needs a stronger reset or when the user asks for options.

Do not average together many templates. Narrow to one anchor quickly.

If the user asks for multiple options, provide 2-4 meaningful directions chosen from `references/typeui-registry/page-type-variants.md`, each with a short explanation of where it fits.

Refresh the local library with `scripts/sync-typeui-registry.ps1` when it looks stale or incomplete.

## Decision Heuristics

### Existing system vs. novelty

- Existing system wins unless the user clearly wants a redesign.
- If redesigning, keep structure and behavior coherent. Do not mix three visual languages on one page.
- If the project has no credible visual language, prefer one anchored template over generic improvisation.

### Color

- Start with neutrals and one main accent.
- Add a second accent only if it encodes a different product meaning.
- Prefer semantic tokens over raw brand-color splashes.
- If borrowing from a template, preserve the contrast logic first; the exact palette can still be adapted.

### Typography

- Create strong contrast between headline, section label, body, and meta text.
- Avoid giant type in app surfaces unless it carries real priority.
- Dense interfaces need smaller but clearer type, not just less spacing.
- Template-led work should inherit the reference template's typographic discipline before inheriting its decoration.

### Layout

- Full-width layouts are often better for operational dashboards.
- Centered narrow columns are often better for narrative or form-heavy flows.
- Cards are optional. Use them only when they clarify grouping.
- If a template suggests a layout pattern, reuse the pattern only when it fits the information architecture.

## References

Read these files as needed:

- `references/surface-playbooks.md`: concrete guidance by screen type
- `references/shadcn-principles.md`: shadcn-friendly direction and theming rules
- `references/anti-ai-patterns.md`: generic AI-UI failure modes and how to replace them
- `references/typeui-registry/catalog.md`: local index of available TypeUI templates
- `references/typeui-registry/page-type-variants.md`: curated mapping from page types to several design directions
- `references/typeui-registry/skills/*.md`: complete preserved TypeUI templates for deep reference

## Output Expectations

When you implement UI changes:

- make the visual direction explicit in the work
- keep the result cohesive across the full screen
- avoid generic filler sections and meaningless stat cards
- ensure labels, controls, and charts are understandable without reading JSON or code
- say which mode you used when the work is substantial
