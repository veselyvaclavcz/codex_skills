# shadcn Principles

These notes distill the official shadcn docs into practical design rules for Codex.

## What matters

- `Open Code`: the component code is meant to be edited. Prefer direct improvement over awkward wrappers.
- `Composition`: primitives and component APIs should stay predictable, reusable, and easy to combine.
- `Beautiful Defaults`: start from clean defaults, then push them into a distinct product feel.
- `AI-Ready`: readable local code and consistent APIs help agents make fewer UI mistakes.

## Design-system implications

- Treat shadcn as a foundation, not as a finished look.
- Reuse local primitives consistently so the UI feels like one system.
- If you need a missing pattern, create it in the same composable style instead of importing a mismatched library.

## Theming guidance

The current docs recommend CSS variables for theming. Use semantic tokens like:

- `background` / `foreground`
- surface-specific tokens such as sidebar, border, ring, chart colors
- custom semantic tokens such as `warning` / `warning-foreground`

This means:

- prefer semantic token names over hardcoded hex values
- define new colors at the token layer when they will recur
- keep contrast decisions centralized

## Style archetypes

Recent shadcn styles are useful as starting directions:

- `Vega`: balanced default product UI
- `Nova`: reduced spacing for compact interfaces
- `Maia`: softer and rounder, more generous spacing
- `Lyra`: sharper, boxier, works with mono or technical feel
- `Mira`: compact and dense

Use these as mood presets, not strict templates.

## Blocks and charts

- Blocks are good starting scaffolds, not the final product.
- If you use a dashboard or auth block, customize spacing, copy, hierarchy, and data density so the result does not look stock.
- shadcn charts are composition-first. Use them with clear labels, explicit time ranges, and restrained chrome.

## RTL and direction-aware layouts

shadcn supports RTL-friendly logical layout patterns. Avoid physical assumptions like left-only or right-only language in component structure when the product may localize.

## Practical rule

When a repo uses shadcn:

1. inspect local tokens and style choices
2. identify the closest existing primitive or block
3. adapt it to the product's actual hierarchy and density
4. keep code readable and easy to modify later

