# CURRENT_TASK: GE-93 — The "Napkin Sketch" / Wireframe

## Ticket Info

- **Jira ID:** GE-93
- **Summary:** The "Napkin Sketch" / Wireframe
- **Type:** Task
- **Priority:** Medium
- **Branch:** `feature/GE-93-the-napkin-sketch-wireframe`
- **Status:** In Progress

## Description

<ticket>
Ett "Low-fidelity" utseende som är väldigt charmigt. Det ser ut som en idé skissad på en servett på ett kafé.

**Maximal Change Title:** Reskin to "Hand-Drawn Sketch / Blueprint" theme

**Description:** Make the entire app look like a rough sketch drawn with a blue ballpoint pen on a paper napkin.

- **Background:** A texture of a white paper napkin or wrinkled notebook paper.
- **Style/Feel:** Lo-Fi / Sketchy. Wobbly lines (scribble effect). Incomplete borders. It should look unfinished and brainstorming-friendly.
- **Colors:** Ink Blue (#00008B) for all lines and text. No other colors, just shading with cross-hatching (streck) for depth.
- **Fonts:** A messy Handwritten font (like *Architects Daughter* or *Permanent Marker*).
- **Cards &amp; Panels:** Look like rough rectangles drawn by hand. Fill backgrounds with a "scribble" fill instead of solid colors.
- **Layout:** Arrows should look hand-drawn with loops and uneven heads.
</ticket>

## Acceptance Criteria

- [x] App has a paper napkin / wrinkled notebook paper background texture (CSS ruled lines + red margin line)
- [x] All text uses a handwritten font (Architects Daughter from Google Fonts)
- [x] Primary color is Ink Blue (#00008B) — no other colors
- [x] Borders/lines look wobbly/sketchy (border-radius: 255px trick, SVG feTurbulence filter defined)
- [x] Cards/panels have rough hand-drawn rectangle appearance with cross-hatch fill (repeating-linear-gradient)
- [x] The theme applies to all Flask-rendered templates (base.html, newsflash/index.html, subscribe.html, thank_you.html, expense_tracker/base.html, expense_tracker/index.html, expense_tracker/summary.html)
- [x] All existing tests pass (383 passed, 12 skipped)
- [x] Linting passes (ruff)

## Files to Modify

Per CLAUDE.md production file map:
- `src/sejfa/newsflash/presentation/templates/base.html` (main base template)
- `src/sejfa/newsflash/presentation/templates/newsflash/index.html`
- `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html`
- `src/sejfa/newsflash/presentation/templates/newsflash/thank_you.html`
- `src/expense_tracker/templates/expense_tracker/base.html`
- `src/expense_tracker/templates/expense_tracker/index.html`
- `src/expense_tracker/templates/expense_tracker/summary.html`

## Progress

| # | Iteration | Action | Result |
|---|-----------|--------|--------|
| 1 | 2026-02-17 | Task initialized, branch created | ✅ |
| 2 | 2026-02-17 | Implemented Napkin Sketch theme in both base templates | ✅ |
| 3 | 2026-02-17 | All 383 tests pass, ruff lint clean | ✅ |

## Notes

- Theme: Hand-Drawn Sketch / Blueprint ("Napkin Sketch")
- Same pattern as GE-86 (GPU overheat) and GE-91 (Claymorphism) — visual theme reskin
- Reference: GE-91 branch `feature/GE-91-the-playful-tactile-3d` for pattern
- Google Fonts to use: `Architects Daughter` (primary) or `Permanent Marker`
- Cross-hatching can be done with CSS `repeating-linear-gradient` patterns
- Wobbly borders: use `border-radius` with irregular values or SVG `feTurbulence` filter
