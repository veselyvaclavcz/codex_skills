# Figma-First Workflow

Use this workflow when the user wants an editable design surface between AI exploration and final code.

## Why Figma-first

This route is better than direct HTML exploration when:

- the user wants to nudge visuals manually
- layout and typography are still unsettled
- multiple variants are needed before implementation
- the user wants to inspect and tune details without touching code

## Recommended loop

1. Choose the screen and the intended job it should do.
2. Pick one anchor direction from TypeUI if the visual language is not settled.
3. Generate an initial draft in Figma with First Draft or Figma Make.
4. Duplicate the frame and branch into a small set of variants.
5. Use AI for large structural changes.
6. Use manual edits for spacing, typography, alignment, emphasis, and grouping.
7. Freeze one winning frame.
8. Pass that frame URL or node ID to Codex through the Figma MCP workflow.
9. Implement in code.
10. If implementation reveals design issues, update the Figma frame and iterate again.

## Tool choice inside Figma

### First Draft

Use First Draft when you need a fast starting point for common web or mobile patterns.

Good for:

- landing pages
- app screens
- settings pages
- dashboards with common structures

Limits:

- weaker for unusual layouts
- not the right tool for precise system-driven implementation
- not a substitute for careful refinement

### Figma Make

Use Figma Make when you want a more active AI collaboration loop with editable outcomes.

Good for:

- refining one part of a selected design
- asking for structural variations
- changing the appearance of an existing frame
- continuing to edit the result manually in Figma

## Variant discipline

Do not create ten weak variants.

Good default:

- one base frame
- one structural variant
- one stylistic variant
- optionally one simplification pass

Kill weak branches quickly.

## What to edit manually

Prompting is a poor tool for:

- tiny spacing adjustments
- visual rhythm
- local hierarchy tuning
- icon balance
- one-off alignment cleanup
- deciding where the eye should land first

Edit those directly in Figma.

## Handoff back to Codex

Once the winning frame is stable:

1. copy the frame or node URL
2. provide it to Codex
3. let Codex use `figma` or `figma-implement-design`
4. validate the implementation against the exact chosen frame

If the user changes the design afterward, treat Figma as the current visual truth and re-run the handoff.
