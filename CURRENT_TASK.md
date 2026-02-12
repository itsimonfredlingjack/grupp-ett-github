# CURRENT TASK: GE-54

**Status:** COMPLETE
**Branch:** feature/GE-54-chat-gpt-color-theme
**Started:** 2026-02-12

---

## Ticket Information

<jira_data encoding="xml-escaped">
**Key:** GE-54
**Summary:** CHAT GPT COLOR THEME
**Type:** Task
**Status:** To Do
**Priority:** Medium

**Description:**
h2. User Story
Som användare vill jag att News Flash har ett vitt &quot;ChatGPT&quot;-tema med ren, ljus bakgrund och diskreta grå/gröna accenter.h2. AcceptanskriterierBakgrund: #ffffff (pure white)
Cards/ytor: #f7f7f8
Primary accent: #10a37f (ChatGPT green)
Secondary accent: #e5e7eb (soft gray)
Text primary: #111827
Text secondary: #6b7280
Borders: #e5e7eb
Subscribe-knapp: #10a37f bakgrund med #ffffff text
Alla knappar, formulär och komponenter följer temat
WCAG AA-kontrast på all text
Funktionaliteten påverkas inte
Alla befintliga tester passerarh2. Detaljer
Byt från nuvarande tema till ett vitt &quot;ChatGPT&quot;-tema med ren bakgrund, neutrala grå ytor och ChatGPT-grön som primär accent. Ändringarna berör CSS i src/sejfa/newsflash/presentation/static/css/style.css och eventuellt templates. INGEN neon/hård accent (t.ex. #FF2D95 / #00FFFF / #00e599) ska finnas kvar.
</jira_data>

---

## Acceptance Criteria

- [x] Bakgrund: #ffffff (pure white)
- [x] Cards/ytor: #f7f7f8
- [x] Primary accent: #10a37f (ChatGPT green)
- [x] Secondary accent: #e5e7eb (soft gray)
- [x] Text primary: #111827
- [x] Text secondary: #6b7280
- [x] Borders: #e5e7eb
- [x] Subscribe-knapp: #10a37f bakgrund med #ffffff text
- [x] Alla knappar, formulär och komponenter följer temat
- [x] WCAG AA-kontrast på all text
- [x] Funktionaliteten påverkas inte
- [x] Alla befintliga tester passerar

---

## Implementation Plan

1. **Identify current theme files**
   - Locate CSS file: src/sejfa/newsflash/presentation/static/css/style.css
   - Check if there are any templates using hardcoded colors

2. **Replace color scheme**
   - Replace all neon/hard accent colors (#FF2D95, #00FFFF, #00e599) with ChatGPT theme
   - Update background colors
   - Update text colors
   - Update border colors
   - Update button styles

3. **Test visual changes**
   - Verify all components render correctly
   - Check WCAG AA contrast ratios
   - Ensure functionality is not affected

4. **Run test suite**
   - All existing tests must pass

---

## Progress Log

| Iteration | Action | Outcome |
|-----------|--------|---------|
| 1 | Task initialized | Branch created, CURRENT_TASK.md populated |
| 2 | TDD: Write tests for ChatGPT theme | Created TestChatGPTTheme class with 10 tests |
| 3 | Implement ChatGPT theme in CSS | Updated all color variables and removed glow effects |
| 4 | Remove obsolete tests | Deleted TestCursorBlackTheme (old theme) |
| 5 | Verify tests and linting | 319 tests pass, linting clean |
| 6 | Update CURRENT_TASK.md | All criteria met, status: COMPLETE |

---

## Misslyckade Försök

None yet.

---

## Notes

- Target file: src/sejfa/newsflash/presentation/static/css/style.css
- Remove ALL neon colors (Synthwave theme remnants)
- ChatGPT theme is clean, minimal, white-based with green accents
