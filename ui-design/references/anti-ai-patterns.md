# Anti-AI Patterns

Use this file as a final pressure test against default AI-generated UI habits.

These are not absolute bans. They are suspicion triggers. If one appears, force yourself to justify it against the product context.

## Layout Smells

- floating detached sidebars with decorative shells
- hero sections inside operational dashboards without a product reason
- center-column SaaS layouts used for data-heavy tools
- default KPI-card mosaics as the first and only dashboard idea
- right rails, glass panels, and detached widgets added only to look "premium"
- asymmetry that creates dead space but not better hierarchy

Replace with:

- clear workspace structure
- practical grouping
- stable navigation and content zones
- dense but readable layouts for product surfaces

## Styling Smells

- oversized radii everywhere
- pill buttons and pill badges as the default shape language
- random gradients, glow haze, conic backgrounds, and blur frosting
- heavy shadows used instead of hierarchy
- blue-purple palettes chosen just because they are easy defaults
- decorative borders or background blobs with no functional role

Replace with:

- tighter shape discipline
- restrained surface treatment
- one accent with semantic purpose
- contrast and typography doing the real hierarchy work

## Content Smells

- decorative eyebrow labels
- empty premium-sounding headlines in product UI
- helper copy that narrates the design instead of the product
- fake metrics, fake charts, and filler cards
- section names like "Operational clarity" or "Live pulse" with no product meaning

Replace with:

- direct product language
- headings that explain the user's job
- data tied to real decisions
- labels that help scanning

## Interaction Smells

- transform-heavy hover effects on routine controls
- motion that exists only to signal polish
- hidden primary actions
- placeholder-only form labels
- chart chrome that makes reading harder

Replace with:

- simple hover and focus feedback
- motion that supports hierarchy or state changes
- obvious actions
- persistent labels
- clear chart framing and controls

## Mobile Smells

- desktop layouts merely stacked into one long page
- tiny tap targets hidden in dense chrome
- cards inside cards inside cards
- long hero copy ahead of the task

Replace with:

- one dominant job per screen
- progressive disclosure
- stronger prioritization
- shorter headings and cleaner tap zones

## Litmus Test

Ask these questions:

- Does this screen still work if I remove the decorative treatments?
- Is this pattern here because the product needs it, or because the model defaulted to it?
- Would a human designer keep this exact structure after a second pass?
- Is there one strong visual idea, or just many familiar AI tricks at once?
