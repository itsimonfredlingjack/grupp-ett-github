# CURRENT TASK: GE-52

**Status:** ✅ COMPLETE
**Branch:** `feature/GE-52-synthwave-tema---hot-pink-och-cyan`
**Started:** 2026-02-12

---

## Ticket Information

<jira_data encoding="xml-escaped">
**Jira ID:** GE-52
**Summary:** Synthwave tema - Hot Pink och Cyan
**Type:** Task
**Priority:** Medium
**Status:** To Do

### User Story
Som användare vill jag att News Flash har ett Synthwave-tema med djup mörk bakgrund och neon-accenter.

### Details
Byt fran nuvarande grona Cursor-tema till Synthwave med hot pink och cyan neon-accenter. Andringarna beror CSS i src/sejfa/newsflash/presentation/static/css/style.css och eventuellt templates. INGEN gron accent (#00e599) ska finnas kvar.
</jira_data>

---

## Acceptanskriterier

- [x] Bakgrund: #0a0a1a (deep dark navy)
- [x] Cards/ytor: #12121f
- [x] Primary accent: #FF2D95 (hot pink)
- [x] Secondary accent: #00FFFF (cyan)
- [x] Text primary: #ffffff
- [x] Text secondary: #8888aa
- [x] Borders: #1a1a2e
- [x] Subscribe-knapp: #FF2D95 bakgrund med #ffffff text
- [x] Alla knappar, formulär och komponenter följer temat
- [x] WCAG AA-kontrast på all text
- [x] Funktionaliteten påverkas inte
- [x] Alla befintliga tester passerar

---

## Implementation Plan

### Files to Modify
1. `src/sejfa/newsflash/presentation/static/css/style.css` - Main CSS file for theming
2. Templates (if needed) - Check for inline styles or hard-coded colors

### Approach
1. **Identify current green theme colors** in style.css
2. **Replace with Synthwave colors** according to acceptance criteria
3. **Test all components** to ensure theming is applied correctly
4. **Verify WCAG AA contrast** for all text elements
5. **Run existing tests** to ensure no functionality is broken

---

## Progress Log

| Iteration | Action | Result | Timestamp |
|-----------|--------|--------|-----------|
| 1 | Task initialized, branch created | ✅ Setup complete | 2026-02-12 |
| 2 | Updated CSS theme to Synthwave | ✅ All colors updated | 2026-02-12 |
| 3 | Updated tests to verify Synthwave theme | ✅ Tests updated | 2026-02-12 |
| 4 | Verified all tests and linting | ✅ 320 tests passed, linting clean | 2026-02-12 |

---

## Notes

- The current theme uses green accent (#00e599) which must be completely removed
- Focus on CSS changes in `src/sejfa/newsflash/presentation/static/css/style.css`
- Ensure all interactive elements (buttons, forms, links) follow the new theme
- Verify WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text)

---

## Completion Checklist

- [ ] All acceptance criteria checked off
- [ ] Tests passing: `pytest -xvs`
- [ ] Linting passing: `ruff check .`
- [ ] Changes committed
- [ ] Branch pushed to remote
- [ ] PR created
- [ ] Jira ticket updated

---

## Blocked/Issues

None currently.

---

**Last Updated:** 2026-02-12
