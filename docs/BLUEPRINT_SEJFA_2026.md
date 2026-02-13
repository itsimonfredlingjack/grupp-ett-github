# SEJFA — Agentic DevOps Loop Blueprint

> **Verifierad:** 2026-02-13 | **Status:** ✅ Operationellt | **Demo-ready:** Ja
>
> Alla siffror i detta dokument är hämtade direkt från systemet via API-anrop
> och CLI-kommandon, inte kopierade från äldre dokument.

---

## 1. Vad är SEJFA?

SEJFA (Secure Enterprise Jira Flask Agent) är ett **Agentic DevOps Loop**-system
som demonstrerar hur en AI-agent (Claude Code) autonomt kan ta en Jira-ticket
hela vägen från backlog till verifierad deploy — utan mänsklig intervention.

Systemet kallas internt "Ralph Wiggum Loop" efter den roliga tanken att
till och med Ralph klarar DevOps med rätt verktyg.

### Loopen i ett nötskal

```
Jira ticket (GE-XXX)
  → /start-task (branch + CURRENT_TASK.md)
    → TDD-implementation (Claude Code)
      → /finish-task (commit + push + PR)
        → CI (lint + test + coverage)
          → Jules AI Review
            → Merge till main
              → Docker → ACR → Azure Container Apps
                → Post-Deploy Health Check
                  → Jira-kommentar (verified/failed)
                    → Self-Healing (om CI failar)
```

---

## 2. Arkitektur

### 2.1 Flask-appen (3-lager)

Alla moduler följer strikt **Clean Architecture** med dependency injection:

| Lager | Ansvar | Exempel |
|-------|--------|--------|
| **Data** | Modeller (dataclass) + Repository (in-memory) | `ExpenseRepository` |
| **Business** | Service med validering, ingen Flask-kunskap | `ExpenseService` |
| **Presentation** | Flask Blueprint + Jinja2 templates | `expense_bp` |

### 2.2 Moduler

| Modul | Sökväg | Funktion |
|-------|--------|----------|
| **Core/Admin** | `src/sejfa/core/` | Admin auth, subscribers CRUD, statistik |
| **Expense Tracker** | `src/expense_tracker/` | Utgiftshantering (full CRUD) |
| **Integrations** | `src/sejfa/integrations/` | Jira REST API-klient (direkt, ej MCP) |
| **Monitor** | `src/sejfa/monitor/` | SocketIO-baserad real-time dashboard |
| **Utils** | `src/sejfa/utils/` | Health check, security |

### 2.3 Endpoints

| Endpoint | Metod | Beskrivning |
|----------|-------|-------------|
| `/` | GET | Root greeting (JSON) |
| `/health` | GET | Health check (används av deploy-verify) |
| `/admin/login` | POST | Admin-inloggning |
| `/admin` | GET | Admin dashboard (auth) |
| `/admin/statistics` | GET | Statistik (auth) |
| `/admin/subscribers` | GET/POST | Lista/skapa subscribers |
| `/admin/subscribers/<id>` | GET/PUT/DELETE | CRUD per subscriber |
| `/admin/subscribers/search` | GET | Sök subscribers |
| `/admin/subscribers/export` | GET | CSV-export |
| `/expenses/` | GET | Expense tracker |
| `/monitor` | GET | Monitor dashboard |

---

## 3. Deployment-arkitektur

### 3.1 Flask-appen → Azure

```
Push till main
  → GitHub Actions (deploy.yml)
    → Azure OIDC Login
      → Docker build + push → Azure Container Registry (ACR)
        → az containerapp update → Azure Container Apps
```

**Det finns INGEN Cloudflare Tunnel.** Azure Container Apps har egen ingress med
dynamiskt FQDN som hämtas via `az containerapp show`.

**Secrets som krävs (GitHub):**

| Secret | Syfte |
|--------|-------|
| `AZURE_CLIENT_ID` | OIDC service principal |
| `AZURE_TENANT_ID` | Azure AD tenant |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription |
| `ACR_NAME` | Container Registry-namn |
| `APP_NAME` | Container App-namn |
| `RESOURCE_GROUP` | Azure Resource Group |

### 3.2 Monitor → Cloudflare Pages

Monitor-dashboarden är **helt separat** från Flask-appen:

- **URL:** https://ralph-monitor.pages.dev/monitor
- **Deploy:** Cloudflare Pages (automatisk)
- **Funktion:** Visar Claude Code:s arbete i real-time via SocketIO
- **Viktigt:** Monitor är INTE en del av loopen — den observerar bara

### 3.3 Deployment-flöde (verifierat)

```
                      ┌─────────────┐
                      │  GitHub Repo │
                      │    (main)    │
                      └──────┬──────┘
                             │ push
                      ┌──────▼──────┐
                      │   CI (ci.yml)│ ← lint + test + coverage
                      └──────┬──────┘
                             │ success
                      ┌──────▼──────┐
                      │ deploy.yml  │ ← Docker → ACR → Azure
                      └──────┬──────┘
                             │ workflow_run completed
                      ┌──────▼──────┐
                      │ post_deploy │ ← health check + Jira comment
                      │ _verify.yml │   eller rollback
                      └─────────────┘
```

---

## 4. CI/CD Pipelines (9 workflows)

### 4.1 Workflow-karta

| # | Workflow | Trigger | Syfte |
|---|----------|---------|-------|
| 1 | `ci.yml` | push main, PR | Lint (ruff) + test (pytest) + coverage |
| 2 | `ci_branch.yml` | push feature/* | Branch-CI, matar self-healing |
| 3 | `deploy.yml` | push main | Docker → ACR → Azure Container Apps |
| 4 | `post_deploy_verify.yml` | workflow_run (deploy) | Health check, Jira-kommentar, rollback |
| 5 | `jules_review.yml` | PR opened/sync | AI code review via Jules API |
| 6 | `jules_health_check.yml` | schedule/dispatch | Validerar Jules-integration |
| 7 | `self_healing.yml` | workflow_run (CI fail) | Klassificerar + auto-fixar CI-failures |
| 8 | `self_heal_pr.yml` | (stöd) | Skapar fix-PR vid self-healing |
| 9 | `cleanup-branches.yml` | workflow_dispatch | Manuell nuke av mergade branches |

### 4.2 Senaste körningar (verifierat 2026-02-13)

**CI (ci.yml):**
| Run | SHA | Titel | Status |
|-----|-----|-------|--------|
| #621 | 44f68e2 | GE-60 Simpson 2 theme (PR #386) | ✅ SUCCESS |
| #620 | 5c97876 | Jules 404 fix (push main) | ✅ SUCCESS |
| #619 | — | Update clone command (PR #385) | ✅ SUCCESS |

**Deploy (deploy.yml):**
| Run | Tid | Titel | Status |
|-----|-----|-------|--------|
| #53 | 12:06–12:08 | Jules 404 fix | ✅ SUCCESS |
| #52 | 10:41–10:42 | Clone command update | ✅ SUCCESS |
| #51 | 10:23–10:25 | Revert Codex false ACs | ✅ SUCCESS |

**Post-Deploy Verify:**
| Run | Status | Anmärkning |
|-----|--------|------------|
| #14 | ❌ FAILURE | Health check OK, men "Extract Jira ticket" failade (commit utan GE-XXX) |
| #13 | ✅ SUCCESS | — |
| #12 | ✅ SUCCESS | — |
| #11 | ✅ SUCCESS | — |

**Jules Review:**
| Run | Branch | Status | Anmärkning |
|-----|--------|--------|------------|
| #509 | feature/GE-60 | ✅ SUCCESS | Senaste — bekräftar Jules 404-fix funkar |
| #508 | patch-1 | ❌ | Manuell patch utan full context |
| #507 | fix/codex-false-acs | ❌ | Revert-commit, inget att reviewera |
| #506 | feature/GE-59 | ❌ | Codex-genererad PR |

**Self-Healing:** Alla senaste runs = `skipped` (korrekt: inga CI-failures att heala)

---

## 5. Jules AI Review

### 5.1 Hur det fungerar

1. PR öppnas/uppdateras → `jules_review.yml` triggas
2. `scripts/jules_payload.py` bygger kompakt `JULES_CONTEXT`-objekt
3. API-anrop till `jules.googleapis.com/v1alpha`
4. Jules analyserar ändrade filer och lämnar review-kommentarer
5. Metrics sparas som artifact (`jules_metrics.json`)

### 5.2 Payload-profiler

| Profil | Användning |
|--------|------------|
| `QUICK_REVIEW` | Standard PR review |
| `HEALING_FIX` | Self-healing fixar |
| `DEEP_REVIEW` | Komplexa ändringar |

### 5.3 Bugfix-historik

- **2026-02-13:** `derive_source_name()` genererade `sources/github-owner-repo`
  (bindestreck) men Jules API förväntar `sources/github/owner/repo` (snedstreck).
  Fixat i commit `5c97876`. Alla runs efter fixet = SUCCESS.

---

## 6. Self-Healing System

### 6.1 Flöde

```
CI failure (ci_branch.yml)
  → self_healing.yml triggas via workflow_run
    → scripts/classify_failure.py klassificerar felet
      → Cooldown-check (undvik spam)
        → Jules får failure context + loggar
          → Fix appliceras → self_heal_pr.yml skapar PR
```

### 6.2 Failure-taxonomi (`classify_failure.py`)

| Kategori | Beskrivning |
|----------|-------------|
| `AUTH` | Autentiseringsproblem |
| `RATE_LIMIT` | API rate limiting |
| `NETWORK` | Nätverksfel |
| `TIMEOUT` | Timeout |
| `CONFIG` | Konfigurationsfel |
| `PERMISSION` | Behörighetsfel |
| `TEST_FAIL` | Testfel |
| `LINT_FAIL` | Linting-fel |
| `TYPE_FAIL` | Typfel |
| `BUILD_FAIL` | Byggfel |
| `FLAKY` | Flaky test |
| `UNKNOWN` | Oklassificerat |

---

## 7. Jira-integration

### 7.1 Projekt

- **URL:** https://fredlingjacksimon.atlassian.net
- **Projekt:** GE (grupp-ett)
- **Board:** Kanban (To Do → In Progress → Done)

### 7.2 Integrationspunkter

| Var | Hur | Syfte |
|-----|-----|-------|
| Claude Code (lokal) | `src/sejfa/integrations/jira_client.py` | Hämta ticket, uppdatera status |
| Post-deploy verify | `post_deploy_verify.yml` (curl + REST API v2) | Kommentera ticket med deploy-status |
| Self-healing | Via Jules context | Inkludera ticket-info i fix-payload |

### 7.3 API-klient (`jira_client.py`)

Direkt REST API-klient (ingen MCP-dependency):
- `get_issue(key)` — Hämta ticket
- `search_issues(jql)` — JQL-sök
- `add_comment(key, body)` — Kommentera (ADF-format)
- `transition_issue(key, name)` — Flytta status
- `test_connection()` — Healthcheck

### 7.4 Senaste tickets (verifierat)

| Ticket | Summary | Status |
|--------|---------|--------|
| GE-60 | SIMPSON 2 THEME | In Progress |
| GE-59 | Ralph Simpson Theme | Done |
| GE-58 | Click To View Theme Template | To Do |
| GE-57 | beer2 theme | Done |
| GE-56 | Beer theme | Done |

---

## 8. Testsvit

### 8.1 Siffror (verifierat 2026-02-13)

| Mätvärde | Resultat |
|----------|----------|
| **Tester insamlade** | 330 |
| **Passerade** | 318 |
| **Överhoppade** | 12 |
| **Misslyckade** | 0 |
| **Coverage-krav (lokal)** | 80% (fail_under) |
| **Coverage-krav (CI)** | 70% |

### 8.2 Testfiler (30 st)

| Katalog | Filer | Testar |
|---------|-------|--------|
| `tests/agent/` | 5 filer | Ralph loop, Jules payload, hooks, classify |
| `tests/core/` | 5 filer | Admin auth, statistics, subscribers, DB |
| `tests/expense_tracker/` | 3 filer | Service, repository, routes |
| `tests/integrations/` | 1 fil | Jira-klient |
| `tests/newsflash/` | 5 filer | Subscription, data, integration, colors |
| `tests/utils/` | 2 filer | Health check, security |
| `tests/` (root) | 2 filer | App factory, news flash |

### 8.3 Markers

```python
@pytest.mark.unit          # Isolerade komponenter
@pytest.mark.integration   # Med externa beroenden
@pytest.mark.e2e           # End-to-end workflows
@pytest.mark.slow          # Långsamma tester
```

### 8.4 Python-versioner i CI

3.10, 3.11, 3.12, 3.13

---

## 9. Agent-infrastruktur

### 9.1 Skills

| Skill | Syfte |
|-------|-------|
| `/start-task` | Hämta Jira-ticket → skapa branch → populera CURRENT_TASK.md |
| `/finish-task` | Verifiera → commit → push → PR → uppdatera Jira |
| `/preflight` | Validera att systemet är redo |

### 9.2 Hooks

| Hook | Syfte |
|------|-------|
| `stop-hook.py` | Quality gate (blockerar om test/lint misslyckas) |
| `monitor_hook.py` | Real-time loop-övervakning |
| `monitor_client.py` | SocketIO-klient för monitor dashboard |
| `prevent-push.py` | Förhindrar direktpush till main |

### 9.3 CURRENT_TASK.md

Agentens externa minne. Innehåller:
- Ticket-info (key, summary, description, ACs)
- Branch-namn
- Framstegstabell (iteration, status, anteckning)
- Misslyckade försök (för att undvika upprepning)

### 9.4 Completion signals (Ralph Loop)

| Signal | Betydelse |
|--------|----------|
| `<promise>DONE</promise>` | Uppgift klar |
| `<promise>BLOCKED</promise>` | Kan ej fortsätta |
| `<promise>FAILED</promise>` | Uppgift misslyckad |

---

## 10. Scripts

| Script | Syfte |
|--------|-------|
| `scripts/jules_payload.py` | Bygger kompakt JULES_CONTEXT för reviews |
| `scripts/classify_failure.py` | Klassificerar CI-failures med taxonomi |
| `scripts/jules_review_api.py` | Jules API-klient (source name: `sources/github/{owner}/{repo}`) |

---

## 11. Kända problem & edge cases

### 11.1 Post-Deploy Verify: commits utan ticket-ID

`post_deploy_verify.yml` extraherar `GE-\d+` från commit-meddelande med `grep -oP`.
Om committen saknar ticket-ID (t.ex. "Fix Jules 404") failar steget pga `pipefail`
i GitHub Actions. Hälsochecken passerar dock, och rollback triggas inte.

**Påverkan:** Kosmetisk (workflow markeras som failed, men deploy fungerar)

**Fix-förslag:** Lägg till `|| true` efter grep-pipen, eller ändra till
`grep -oP 'GE-\d+' || echo ""` utan pipeline.

### 11.2 Jules Review: failures före 404-fix

Alla Jules Review-runs före commit `5c97876` (2026-02-13 12:06) failade med 404.
Det är förväntat — buggen fanns i `derive_source_name()`. Alla runs efter fixet fungerar.

### 11.3 Codex (OpenAI) incident

PR #383 skapades av Codex för GE-59. Codex markerade falskt AC1-AC9 som completed
i CURRENT_TASK.md. Reverterat via PR #384.

---

## 12. Kodstil & verktyg

| Verktyg | Konfiguration |
|---------|---------------|
| **Linter** | Ruff (E, F, W, I, N, UP, B, C4) |
| **Radlängd** | 88 tecken (Black-kompatibel) |
| **Target** | Python 3.10 |
| **Type hints** | Alla funktionssignaturer |
| **Docstrings** | Google-stil |
| **Imports** | stdlib → third-party → local |
| **Namngivning** | snake_case / PascalCase / SCREAMING_SNAKE_CASE |

### Commit-format

```
GE-XXX: Kort beskrivning (max 72 tecken)

- Detaljpunkt 1
- Detaljpunkt 2

Co-Authored-By: Claude Code <noreply@anthropic.com>
```

### Branch-namngivning

```
feature/GE-XXX-kort-beskrivning
fix/GE-XXX-kort-beskrivning
```

---

## 13. Säkerhet

### Tillåtet

- Läsa/skriva kod i src/, tests/, docs/
- Köra tester och linting
- Skapa commits och branches
- Läsa Jira-tickets via direkt API
- Skapa PR via `gh` CLI

### Förbjudet

- Installera paket utan godkännande
- Skriva credentials/secrets i kod
- Ändra .github/CODEOWNERS utan godkännande
- Ändra .claude/hooks/ utan godkännande
- Destruktiva kommandon (rm -rf, reset --hard, push --force)
- Pusha till main direkt (endast via PR)
- Skippa hooks (--no-verify)

### Prompt injection-skydd

All Jira-data omsluts i `<ticket>`/`<requirements>`-taggar i CURRENT_TASK.md
och behandlas som DATA, aldrig som instruktioner.

---

## 14. Filstruktur

```
grupp-ett-github/
├── app.py                          # Flask create_app factory
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Ruff, pytest, coverage config
├── Dockerfile                      # Python 3.12-slim production image
├── src/
│   ├── sejfa/
│   │   ├── core/                   # Admin auth, subscriber service
│   │   ├── integrations/           # Jira REST API-klient
│   │   ├── monitor/                # SocketIO monitor dashboard
│   │   └── utils/                  # Health check, security
│   └── expense_tracker/
│       ├── data/                   # Expense model + repository
│       ├── business/               # ExpenseService
│       └── presentation/           # Blueprint + templates
├── tests/                          # 330 tester (30 filer)
├── scripts/                        # Jules payload, classify, review API
├── static/                         # Frontend (monitor.html, CSS, bilder)
├── docs/                           # Dokumentation
├── .claude/                        # Agent skills, hooks, config
│   ├── commands/                   # preflight.md
│   ├── hooks/                      # stop, monitor, prevent-push
│   ├── skills/                     # start-task, finish-task
│   └── ralph-config.json           # Ralph loop config
└── .github/workflows/              # 9 CI/CD pipelines
```

---

## 15. Demo-checklista (Måndag)

### Före demo

- [ ] Verifiera att Azure Container App svarar på /health
- [ ] Kolla att senaste deploy i GitHub Actions är grön
- [ ] Ha en Jira-ticket redo i "To Do" (t.ex. GE-58 eller ny)
- [ ] Monitor öppen: https://ralph-monitor.pages.dev/monitor
- [ ] Claude Code redo med repo klonat

### Demo-flöde

1. **Visa Jira-board** — tickets i To Do / In Progress / Done
2. **Kör `/start-task GE-XXX`** — Claude hämtar ticket, skapar branch
3. **Visa CURRENT_TASK.md** — agentens externa minne
4. **TDD-cykel** — test först → fail → implement → pass
5. **Kör `/finish-task`** — auto commit, push, PR
6. **Visa GitHub Actions** — CI kör, Jules reviewar
7. **Merge PR** — deploy triggas automatiskt
8. **Visa post-deploy verify** — health check, Jira-kommentar
9. **Visa Jira-ticket** — automatisk deploy-kommentar

### Backup: Om något inte funkar

| Problem | Åtgärd |
|---------|--------|
| Azure nere | Visa CI + Jules review-delen av loopen |
| Jules 404 | Kolla att source name matchar i jules_review_api.py |
| CI failar | Visa self-healing workflow (triggas automatiskt) |
| Jira API nere | Visa loopen utan Jira-steg, förklara integration |

---

*Senast uppdaterad: 2026-02-13 av Cockpit-Claude (verifierat mot live-system)*
