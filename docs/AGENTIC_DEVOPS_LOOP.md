# AGENTIC DEVOPS LOOP — OPERATIV DOKUMENTATION

> Single source of truth för grupp-ett-github (SEJFA).
> Senast verifierad: 2026-02-11 mot faktisk repo-audit.
> Alla påståenden i detta dokument är verifierade mot repots faktiska innehåll om inte markerade med ⚠️.

---

## 1. SYSTEMÖVERSIKT

### Vad det ÄR

En Flask-applikation ("SEJFA") med en agentic DevOps-loop byggd ovanpå Claude Code. Hela idén är att automatisera flödet från Jira-ticket till deploy utan manuell intervention.

### Vad som BORDE hända

```
Jira ticket (GE-xxx)
    → /start-task hämtar ticket, skapar branch, sätter upp CURRENT_TASK.md
    → Ralph Loop (TDD: red → green → refactor, repeat)
    → /finish-task verifierar kvalitet, pushar, skapar PR
    → CI kör (lint + test)
    → Jules AI reviewar PR
    → Auto-merge
    → deploy.yml bygger Docker → ACR → Azure Container Apps
    → Live
```

### Vad som FAKTISKT händer

```
Jira ticket (GE-xxx)
    → /start-task ✅ funkar (med reservation, se CURRENT_TASK.md-problemet)
    → Ralph Loop ✅ funkar (stop-hook är fail-closed och solid)
    → /finish-task ⚠️ OKLART — Claude kan avsluta INNAN finish-task körs (se Problem 1)
    → CI kör ✅ funkar (ci.yml + ci_branch.yml)
    → Jules AI reviewar ❓ OVERIFIERAT — alla 4 Jules-workflows beror på en action-referens som kan vara ogiltig
    → Auto-merge ❌ SAKNAS — inget mergar PRn
    → deploy.yml ✅ triggas av merge till main — men ingen merge sker automatiskt
    → Monitor-dashboard ❌ DÖD — trasiga imports, får inga uppdateringar
```

---

## 2. DETALJERAD STATUSRAPPORT

### ✅ VAD SOM FUNKAR

#### Ralph Loop (stop-hook)
Filen: `.claude/hooks/stop-hook.py`

Stop-hooken är **fail-closed** och väldesignad:
- Tre persistence-mekanismer: `.ralph_loop_active`, `ralph-state.json`, `.git/info/ralph-loop-active.json`
- Återskapar borttagna flaggfiler mitt i loopen (förhindrar bypass)
- Enforcar på Jira-style branches (`feature/GE-*`) även utan explicit loop-flagga
- Max 25 iterationer med auto-WIP-commit + draft PR som säkerhetsventil
- Ogiltig JSON / tom input medan loop är aktiv = blockerar (förhindrar bypass)
- Exit code 2 = "fortsätt jobba" när loop är aktiv

#### CI Pipeline
Filer: `.github/workflows/ci.yml`, `.github/workflows/ci_branch.yml`

- `ci.yml`: Triggas på push till `main` och PRs mot `main`. Kör ruff lint + pytest på Python 3.10-3.13. Coverage gate 70%.
- `ci_branch.yml`: Samma sak men för non-main branches.
- Fungerar som förväntat.

#### Deploy Pipeline
Fil: `.github/workflows/deploy.yml`

- Triggas på push till `main`
- Bygger Docker image → pushar till Azure Container Registry → deployer till Azure Container Apps
- Fungerar — MEN triggas bara om något mergas till main, vilket inte sker automatiskt.

#### Branch Cleanup
Fil: `.github/workflows/cleanup-branches.yml`

- Daglig cleanup (03:00 UTC) av mergade branches äldre än 7 dagar
- Fungerar som förväntat.

#### Applikationsarkitektur
Tre-lager Flask-app med ren separation:
- `src/sejfa/newsflash/` — data/business/presentation (SQLAlchemy)
- `src/expense_tracker/` — data/business/presentation (in-memory)
- `src/sejfa/core/` — admin auth, subscriber service (legacy)
- `src/sejfa/monitor/` — monitor service + routes (server-sidan finns men hooks skickar inget)

243 tester. SQLAlchemy + Flask-Migrate. Gunicorn.

---

### ❌ VAD SOM INTE FUNKAR

#### Problem 1: Claude avslutar innan /finish-task körs

**Symptom:** Claude Code tycker den är klar (tester passerar, kod skriven) och avslutar sessionen. Stop-hooken fångar inte upp detta. Ingen PR skapas.

**Analys:**
Stop-hooken i sig är solid (fail-closed). Men den kan bara fånga **stopp-events**. Problemet är troligen att Claude Codes interna completion-heuristik triggar **innan** ett stopp-event skickas. Det finns tre möjliga orsaker:

1. **Claude bestämmer sig internt** — Claude Code har en intern gräns för turns och en heuristik för "uppgiften verkar klar". Om den bestämmer sig för att sluta skicka kommandon och istället producera en sammanfattning, triggas aldrig något stopp-event, och hooken körs aldrig.

2. **Hooken returnerar exit 0 i edge cases** — Även om hooken är designad fail-closed, finns det kodstigar där den returnerar 0 (t.ex. om loopen inte är aktiv). Om loop-aktiveringen failar vid start har hooken inget att enforcea.

3. **Hooken blockar men Claude ignorerar den** — Om hooken returnerar exit 2 men Claude Code inte respekterar det korrekt, avslutas sessionen ändå.

**Status:** ⚠️ Ej löst. Kräver debugging med faktisk Claude Code-session för att fastställa vilken orsak det är.

#### Problem 2: PRs mergas aldrig automatiskt

**Symptom:** Även om finish-task lyckas skapa en PR, stannar flödet. Ingen merge sker.

**Analys:**
`finish-task` SKILL.md definierar `gh pr create` men innehåller INGEN merge-logik. Det finns ingen workflow som mergar PRs efter CI + review passerat. Flödet bryter vid:

```
PR skapad → CI kör ✅ → Jules reviewar ❓ → [INGENTING] → merge sker aldrig → deploy triggas aldrig
```

**Fix som behövs (välj en):**
- A) Lägg till `gh pr merge --auto --squash` i finish-task (enklast — GitHub mergar när checks passerar)
- B) Ny GitHub Actions workflow som mergar efter Jules approve + CI pass
- C) Aktivera branch protection med "auto-merge" i GitHub repo settings + A

#### Problem 3: Monitor-dashboard är död

**Symptom:** Dashboarden på `gruppett.fredlingautomation.dev/static/monitor.html` visar inget.

**Analys:**
Två hooks ska skicka uppdateringar till dashboarden:
- `.claude/hooks/monitor_hook.py` (PreToolUse) — ska skicka tool-use events
- `.claude/hooks/stop-hook.py` — ska skicka status vid stopp

Båda importerar från `monitor_client.py` som ligger i samma mapp. Men **Python hittar inte filen** pga trasig import-path. Importen wrappas i try/except → `MONITOR_AVAILABLE = False` → alla monitor-anrop skippas tyst.

**Fix:** Lägg till `sys.path.insert(0, os.path.dirname(__file__))` innan importen i båda hooks, eller ändra till relativ import.

#### Problem 4: Jules-integration är overifierad

**Symptom:** Oklart om Jules AI-review fungerar överhuvudtaget.

**Analys:**
4 workflows beror på `google-labs-code/jules-action@v1.0.0`:
- `jules_review.yml` — AI code review på PRs
- `jules_health_check.yml` — daglig health ping
- `self_healing.yml` — auto-fix vid CI-fail
- `self_heal_pr.yml` — manuell self-heal

Problem:
1. **Action-referensen kan vara ogiltig** — `google-labs-code/jules-action@v1.0.0` kanske inte existerar eller har bytt namn. Om den inte finns failar ALLA Jules-workflows.
2. **`scripts/preflight.sh` SAKNAS** — `jules_health_check.yml` rad 52 kör `bash scripts/preflight.sh` men filen finns inte i repot. Health check kraschar varje körning.
3. **Säkerhetsrisk i `self_healing.yml`** — har `contents: write` permissions + checkout av `head_sha` från potentiella forks = RCE-risk.

**Status:** ⚠️ Kräver verifiering. Kolla GitHub Actions run-historik för att se om Jules-workflows faktiskt har körts framgångsrikt.

#### Problem 5: CURRENT_TASK.md-inkonsistens

**Symptom:** Hooks och skills pekar på olika filer.

**Analys:**
- `start-task` SKILL.md populerar `CURRENT_TASK.md`
- `prevent-push.py` hook läser `CURRENT_TASK.md` (rot-mappen)
- Det fanns TVÅ filer: `CURRENT_TASK.md` (GE-49) och en gammal kopia i `docs/` (GE-40)
- De beskriver OLIKA tasks

**Fix:** Bestäm EN plats. Uppdatera alla skills och hooks att peka på samma fil.

---

### ⚠️ SÄKERHETSPROBLEM

1. **Hardcoded credentials** — `src/sejfa/core/admin_auth.py` har default admin/admin123
2. **`self_healing.yml` RCE-risk** — `contents: write` + checkout av untrusted code
3. **Flask secret key** — troligen hardcoded i `app.py` (ej verifierat i audit men flaggat tidigare)

---

## 3. FILKARTA

### Workflows (8 st)
| Fil | Status | Funktion |
|-----|--------|----------|
| `ci.yml` | ✅ | Lint + test på PRs/push till main |
| `ci_branch.yml` | ✅ | Lint + test på feature branches |
| `deploy.yml` | ✅ (men triggas aldrig pga ingen merge) | Docker → ACR → Azure |
| `cleanup-branches.yml` | ✅ | Städar mergade branches dagligen |
| `jules_review.yml` | ❓ Overifierad | AI code review på PRs |
| `jules_health_check.yml` | ❌ Trasig (preflight.sh saknas) | Daglig Jules health ping |
| `self_healing.yml` | ❓ Overifierad + säkerhetsrisk | Auto-fix vid CI-fail |
| `self_heal_pr.yml` | ❓ Overifierad | Manuell self-heal per PR |

### Hooks (4 st)
| Fil | Status | Funktion |
|-----|--------|----------|
| `stop-hook.py` | ✅ Logiken funkar, ❌ monitor-import trasig | Ralph Loop enforcer |
| `monitor_hook.py` | ❌ Import trasig, gör inget | Ska skicka tool-use events till dashboard |
| `monitor_client.py` | ❌ Hittas inte av hooks | HTTP-klient för monitor API |
| `prevent-push.py` | ⚠️ Läser fel CURRENT_TASK.md | Blockerar push vid no-push markers |

### Skills (2 st)
| Fil | Status | Funktion |
|-----|--------|----------|
| `start-task/SKILL.md` | ⚠️ Skriver till fel CURRENT_TASK.md | Hämtar Jira ticket, skapar branch |
| `finish-task/SKILL.md` | ⚠️ Saknar merge-logik | Verifierar kvalitet, skapar PR |

### Scripts (3 st)
| Fil | Status | Funktion |
|-----|--------|----------|
| `scripts/ci_check.sh` | ✅ | Lokal CI-simulering |
| `scripts/classify_failure.py` | ✅ (kod ok, beroende på Jules) | Klassificerar CI-fel |
| `scripts/jules_payload.py` | ✅ (kod ok, beroende på Jules) | Bygger Jules-payload |
| `scripts/preflight.sh` | ❌ SAKNAS | Refereras av jules_health_check.yml |

### Docs (viktigast)
| Fil | Status | Beskrivning |
|-----|--------|-------------|
| `docs/AGENTIC_DEVOPS_LOOP.md` | 📌 DENNA FIL | Single source of truth |
| `docs/jules-playbook.md` | ❓ Overifierad mot workflows | Jules drifthandbok |
| `docs/DEPLOYMENT.md` | ⚠️ Cloudflare Tunnel-specifik | Deploy-guide |
| `CURRENT_TASK.md` (rot) | ⚠️ Inkonsistent med docs/ | Aktiv task (GE-49) |
| Tidigare `docs/`-kopia | ✅ Borttagen | Tidigare dubblett av task-fil |

---

## 4. INSTRUKTIONER FÖR AI-AGENTER

### För Claude Code (implementation)
1. Läs DENNA fil först — den beskriver verkligheten
2. `.claude/CLAUDE.md` har kodstil och arkitekturregler
3. Skills finns i `.claude/skills/` — följ dem men var medveten om CURRENT_TASK.md-inkonsistensen
4. Stop-hooken fungerar — lita på den, men kör alltid `/finish-task` explicit
5. Monitor-hooks skickar INGET just nu — ignorera monitor-uppdateringar tills import-fixen är på plats

### För Jules (code review)
1. `docs/jules-playbook.md` finns men är ⚠️ OVERIFIERAD
2. Payload byggs av `scripts/jules_payload.py`
3. Fel klassificeras av `scripts/classify_failure.py`
4. Om `google-labs-code/jules-action@v1.0.0` inte fungerar — inget av detta spelar roll

### För Cockpit-Claude (orchestration)
1. Lita BARA på denna fil för systembeskrivning
2. Repot finns på: `https://github.com/itsimonfredlingjack/grupp-ett-github.git`
3. Förväxla INTE med Simons privata repo: `https://github.com/itsimonfredlingjack/agentic-dev-loop-w-claude-code-and-github-actions.git`
4. Deploy sker via Cloudflare Tunnel → `gruppett.fredlingautomation.dev`

---

## 5. PRIORITERAD FIX-LISTA

| # | Problem | Svårighetsgrad | Impact |
|---|---------|---------------|--------|
| 1 | Auto-merge saknas | Enkel (`gh pr merge --auto`) | Hela kedjan bryter utan detta |
| 2 | Monitor imports trasiga | Enkel (sys.path fix) | Dashboard helt död |
| 3 | CURRENT_TASK.md inkonsistens | Enkel (bestäm en plats) | Skills och hooks tittar på olika filer |
| 4 | preflight.sh saknas | Enkel (skapa filen eller ta bort referensen) | Jules health check kraschar |
| 5 | Verifiera Jules action-referens | Kolla Actions-historik | Om ogiltig funkar inget Jules-relaterat |
| 6 | Claude avslutar innan finish-task | Svår (kräver debugging) | PRs skapas aldrig |
| 7 | self_healing.yml säkerhetsrisk | Medium (ta bort contents: write) | RCE-risk |
| 8 | Hardcoded credentials | Medium | Säkerhetsrisk |

---

## 6. CHANGELOG

| Datum | Ändring |
|-------|---------|
| 2026-02-11 | Skapad baserat på fullständig repo-audit. Ersätter alla tidigare fragmenterade docs som operativ referens. |
