# CURRENT TASK: GE-36

**Status:** 🟡 IN PROGRESS
**Branch:** `feature/GE-36-cursorflash-mvp`
**Started:** 2026-02-05

---

## Ticket Information

<ticket>
**JIRA ID:** GE-36
**Type:** Task
**Priority:** Medium
**Status:** To Do

**Summary:** MVP: Cursorflash – Snabba nyheter med "Neon/Cyberpunk"-tema

**Description:**

Beskrivning: Vi behöver få upp Cursorflash ASAP. Det är en enkel app för att posta korta nyhetsflashes. Inga skelett eller placeholders – vi bygger en fungerande "Single Page"-känsla direkt.

Design &amp; UI (Viktigt!):
- Hero-text: Längst upp ska det stå exakt: &quot;Hello Gemini Claude Cursor Codex world&quot; i stor text.
- Stil: &quot;Sexiga färger&quot;. Tänk mörkt tema, neon-lila/cyan accenter (Cyberpunk-vibe). CSS ska vara inline eller minimal style.css.

User Story: Som användare vill jag kunna posta nyhetsflashes via Cursorflash så att jag kan broadcasta uppdateringar till teamet i realtid.

Data &amp; Modell (Flash):
- id (int)
- content (str) – Själva meddelandet.
- severity (int) – Hur allvarlig flashen är (1-5).

Affärsregler (TDD dessa först!):
1. Längd-check: content får inte vara tomt och max 280 tecken (Twitter-style).
2. Severity-check: severity måste vara ett heltal mellan 1 och 5. Om det är utanför spannet ska det kastas ett error.

Tekniska Constraints (Strict Clean Arch): Följ 3-lagersmodellen slaviskt.
1. Data: InMemoryFlashRepository.
2. Business: FlashService (Ingen Flask här!). Injecta repot i __init__.
3. Presentation: Flask Blueprint.
   - GET / – Visar formulär + lista på alla flashes.
   - POST /add – Tar emot form data, validerar via Service, redirectar hem.
   - GET /clear – (Dev route) Rensar minnet/listan så man kan börja om.

Dev Notes: Kör sqlite:///:memory: så vi slipper migrations-strul. Fokusera på att få upp flödet: Test -&gt; Kod -&gt; UI. Kör hårt.
</ticket>

---

## Acceptance Criteria

- [x] TDD: Unit-tester för reglerna (längd & severity) är gröna.
- [x] App Factory (`create_app`) sätter ihop lagren korrekt.
- [x] UI är på svenska ("Lägg till", "Felaktigt värde" etc).
- [x] Startsidan har den specifika "Hello Gemini..."-texten och ser modern ut.

---

## Implementation Plan

### Phase 1: Data Layer (TDD)
1. Create `Flash` dataclass/model with `id`, `content`, `severity`
2. Create `InMemoryFlashRepository` with:
   - `add(flash: Flash) -> Flash`
   - `get_all() -> List[Flash]`
   - `clear() -> None`

### Phase 2: Business Layer (TDD)
1. Create `FlashService` with dependency injection
2. Implement validation rules:
   - Content: non-empty, max 280 chars
   - Severity: 1-5 range
3. Methods:
   - `create_flash(content: str, severity: int) -> Flash`
   - `get_all_flashes() -> List[Flash]`
   - `clear_flashes() -> None`

### Phase 3: Presentation Layer
1. Create Flask Blueprint with routes:
   - `GET /` - Display form + flash list
   - `POST /add` - Handle form submission
   - `GET /clear` - Clear all flashes
2. Create template with:
   - Hero text: "Hello Gemini Claude Cursor Codex world"
   - Cyberpunk styling (dark theme, neon purple/cyan)
   - Swedish UI text
3. Integrate into `create_app` factory

### Phase 4: Integration & Polish
1. Verify all acceptance criteria
2. Run full test suite
3. Run linting
4. Manual testing

---

## Progress Log

| Iteration | Action | Outcome | Tests | Next Step |
|-----------|--------|---------|-------|-----------|
| 1 | Task initialized | Branch created | - | Start Phase 1 TDD |
| 2 | Phase 1-3 complete | All layers implemented via TDD | 228/228 ✅ | Commit & push |

---

## Misslyckade Försök

_(None yet)_

---

## Exit Criteria (ALL must be true)

- [ ] All acceptance criteria checked off
- [ ] All tests pass: `pytest -xvs`
- [ ] No linting errors: `ruff check .`
- [ ] Changes committed with proper format
- [ ] Branch pushed to remote
- [ ] PR created

---

**IMPORTANT:** This file is the agent's persistent memory. Update after every iteration.
