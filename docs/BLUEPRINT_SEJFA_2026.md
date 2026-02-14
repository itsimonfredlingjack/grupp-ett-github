# SEJFA Blueprint 2026

**Repo:** `itsimonfredlingjack/grupp-ett-github`
**Branch:** `main`
**Last verified:** 2026-02-13
**Maintainer:** Simon Fredling Jack — AI Automation Architect

---

## 1. What SEJFA Is

Flask-applikation med en agentic DevOps-loop ("Ralph Wiggum Loop").
Fyra moduler: Admin dashboard, subscriber management, expense tracker, real-time monitor.
Loopen drivs lokalt via Claude Code på Simons dev-maskin — inte via Docker, inte via cockpit MCP.

### Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.10–3.13 |
| Framework | Flask (create_app factory i `app.py`) |
| Architecture | Clean 3-Layer (Data → Business → Presentation) |
| Agent | Claude Code (Ralph Loop) |
| AI Review | Google Jules (API-direkt + GitHub Action) |
| CI/CD | GitHub Actions (9 workflows) |
| Deploy target | Azure Container Apps |
| Registry | Azure Container Registry (OIDC auth) |
| Monitoring | Cloudflare Pages (`ralph-monitor.pages.dev`, separat) |

---

## 2. Architecture — Clean 3-Layer

Varje modul följer strikt lageruppdelning:

```
Data         → Modeller (dataclass) + Repository (in-memory)
Business     → Service med validering (INGEN Flask här)
Presentation → Flask Blueprint + Jinja2 templates
```

Dependency injection: Services får repository via `__init__`.

### Projektstruktur

```
grupp-ett-github/
├── app.py                      # Flask entry (create_app factory)
├── requirements.txt
├── pyproject.toml               # Ruff, pytest, coverage config
├── Dockerfile                   # Python 3.12-slim
├── src/
│   ├── sejfa/
│   │   ├── core/                # Admin auth, subscriber service
│   │   ├── integrations/        # Jira API-klient (direkt REST)
│   │   ├── monitor/             # Real-time monitoring (SocketIO)
│   │   └── utils/               # Health check, security
│   └── expense_tracker/
│       ├── data/                # Expense model + repository
│       ├── business/            # ExpenseService
│       └── presentation/        # Blueprint + templates
├── tests/                       # 318+ tester
├── scripts/                     # Workflow helpers
│   ├── jules_payload.py         # Bygger kompakt Jules-kontext
│   ├── jules_review_api.py      # Direkt Jules REST API-klient
│   ├── classify_failure.py      # CI failure taxonomy
│   ├── preflight.sh             # Health check prereqs
│   └── ci_check.sh              # CI status helper
├── .claude/                     # Agent config (skills, hooks, commands)
├── .github/workflows/           # 9 CI/CD workflows
├── memory/                      # Persistent context (CLAUDE.md integration)
└── docs/                        # Dokumentation (denna fil)
```

---

## 3. The Ralph Wiggum Loop

Kör LOKALT på Simons dev-maskin via Claude Code. Inte serverbaserad.

```
Jira ticket (GE-XXX)
  → /start-task    (preflight, branch, CURRENT_TASK.md)
  → TDD-cykel      (test → FAIL → implement → PASS → refactor)
  → /finish-task:
      1. pytest -xvs --cov=src --cov=app.py --cov-fail-under=80
      2. ruff check . && ruff format --check .
      3. git add -A && git commit -m "GE-XXX: ..."
      4. git push -u origin {branch}
      5. gh pr create
      6. gh pr checks --watch  (väntar på ci.yml)
      7. gh pr merge --squash
      8. Jira → Done
      9. <promise>DONE</promise>
```

### Hooks

| Hook | Fil | Funktion |
|------|-----|----------|
| stop-hook | `.claude/hooks/stop-hook.py` | Blockerar exit tills `<promise>DONE</promise>` + quality gates |
| prevent-push | `.claude/hooks/prevent-push.py` | Blockerar push om CURRENT_TASK.md har no-push markers |

### Completion Signals

| Signal | Betydelse |
|--------|----------|
| `<promise>DONE</promise>` | Uppgift helt klar |
| `<promise>BLOCKED</promise>` | Kan ej fortsätta, behöver hjälp |
| `<promise>FAILED</promise>` | Uppgiften kan ej slutföras |

---

## 4. GitHub Actions Pipeline — 9 Workflows

### Pipeline Flow

```
Push till feature-branch
  → ci_branch.yml (test matrix 3.10-3.13 + lint + security)

PR mot main
  → ci.yml (REQUIRED CHECK — gh pr checks väntar på denna)
  → jules_review.yml (AI code review via Jules API)

Merge till main
  → deploy.yml (Azure OIDC → ACR build → Container Apps deploy)
  → post_deploy_verify.yml (health check → Jira comment ELLER rollback)

CI failure
  → self_healing.yml (Jules auto-fix, max 3 retries, 30-min cooldown)

On-demand
  → self_heal_pr.yml (manuell Jules healing via label eller dispatch)
  → cleanup-branches.yml (kräver "DELETE ALL BRANCHES" bekräftelse)

Scheduled
  → jules_health_check.yml (daglig 06:00 UTC, ping Jules API)
```

### Workflow Reference

| # | Workflow | Trigger | Purpose |
|---|---------|---------|--------|
| 1 | `ci.yml` | push main, PR main | **Required check.** Test matrix (3.10-3.13), lint, security, coverage ≥80% |
| 2 | `ci_branch.yml` | push non-main | Samma tester som ci.yml men mot feature branches |
| 3 | `jules_review.yml` | PR opened/ready/synchronize | AI code review via Jules REST API (direkt) |
| 4 | `deploy.yml` | push main | Azure OIDC → ACR build+push → Container Apps deploy |
| 5 | `post_deploy_verify.yml` | deploy completed | Health check med retries → Jira comment ELLER auto-rollback |
| 6 | `self_healing.yml` | CI completed (failure) | Auto-fix via Jules action, cooldown 30 min, max 3 retries |
| 7 | `self_heal_pr.yml` | dispatch / label `jules-heal` | Manuell self-healing för specifik PR |
| 8 | `jules_health_check.yml` | cron 06:00 UTC / dispatch | Daglig Jules API connectivity check |
| 9 | `cleanup-branches.yml` | dispatch (med bekräftelse) | Stäng alla PRs + radera alla branches utom main |

---

## 5. CI — Tester & Kodkvalitet

### ci.yml (Required Check)

Tre parallella jobb:

**test** — Matrix: Python 3.10, 3.11, 3.12, 3.13
```bash
ruff check . --output-format=github
pytest -xvs --cov=src --cov=app.py --cov-report=xml --cov-report=term-missing --cov-fail-under=80
```

**lint** — Python 3.12
```bash
ruff check . --output-format=github
ruff format --check .
```

**security** — Python 3.12
```bash
safety check --full-report   # continue-on-error: true
```

Coverage upload till Codecov sker på Python 3.12 (fail_ci_if_error: false).

### Coverage Scope — Synkroniserad

Alla tre coverage-runners använder identisk scope sedan 2026-02-13:

| Runner | Scope | Threshold |
|--------|-------|----------|
| ci.yml | `--cov=src --cov=app.py` | 80% |
| ci_branch.yml | `--cov=src --cov=app.py` | 80% |
| finish-task (lokal) | `--cov=src --cov=app.py` | 80% |

### Ruff Config (pyproject.toml)

| Setting | Value |
|---------|------|
| Line length | 88 (Black-kompatibel) |
| Rules | E, F, W, I, N, UP, B, C4 |
| Target | Python 3.10 |
| Exclude | `.claude/hooks/*`, `venv`, `.venv` |

### Test Stats

| Metric | Value |
|--------|------|
| Total tests | 318+ |
| Skipped | ~12 |
| Framework | pytest |
| Markers | `@pytest.mark.unit`, `.integration`, `.e2e`, `.slow` |

---

## 6. Jules Review — AI Code Review

### Modes

Jules kör i **två separata modes**:

**Mode 1: API-Direct Review (jules_review.yml)**
Använder `scripts/jules_review_api.py` som gör REST-anrop direkt till `jules.googleapis.com/v1alpha`. Postar review-kommentarer som GitHub PR comments. Skapar INGA pull requests.

**Mode 2: Action-Based Healing (self_healing.yml + self_heal_pr.yml)**
Använder `google-labs-code/jules-action@v1.0.0` som skapar en Jules-session med `automationMode`. Jules kan göra kodändringar som committas och pushas.

### jules_review_api.py — Return Codes

Designprincip: Infrastrukturfel blockerar INTE merges. Bara reella review-failures blockerar.

| Return Code | Situation | Effekt |
|-------------|-----------|-------|
| 1 | Missing API key eller repo/PR | Blockerar (config error) |
| 0 | API unavailable / connection error | Postar warning-kommentar, blockerar EJ |
| 0 | Unexpected API response (inget session ID) | Postar warning-kommentar, blockerar EJ |
| 0 | Session timeout (9 min) | Postar timeout-kommentar, blockerar EJ |
| 1 | Session state = FAILED | Blockerar (reellt review-problem) |
| 0 | Review completed | Postar findings |

### jules_review.yml — Commit Status

Steget "Set Jules review status" sätter ALLTID `STATE="success"` oavsett Jules-outcome:

| Jules Outcome | Status | Description |
|---------------|--------|------------|
| success | success | "Jules review completed (API direct)" |
| skipped | success | "Jules review skipped" |
| failure | success | "Jules review had issues (see PR comment for details)" |

Detta säkerställer att Jules-infrastrukturproblem aldrig blockerar merges.

### 5 Anti-Spam Layers

Förhindrar att Jules triggar sig själv eller kör onödigt:

| Layer | Mechanism |
|-------|----------|
| 1. Concurrency | `cancel-in-progress: true` per PR-nummer |
| 2. SHA-dedup | Kollar om successful run redan finns för samma `head_sha` |
| 3. Bot-actor block | `github.actor != 'google-labs-jules[bot]'` |
| 4. Branch-prefix block | 6 patterns: `jules-*`, `review/*`, `update-pr-review*`, `automated-review*`, `pr-review-*`, `review-findings*` |
| 5. Commit-author check | Skippar om `git log -1 --format='%an'` innehåller `[bot]` |

Dessutom: commit messages med `[skip-jules-review]` bypasas review.

---

## 7. Self-Healing System

### self_healing.yml (Automatisk)

Triggas av `workflow_run` completion (CI = failure):

```
CI failure
  → Secret check (JULES_API_KEY)
  → Checkout failed revision
  → Collect failure capsule (sista 60 rader log)
  → classify_failure.py → taxonomy + failing targets
  → Cooldown check (30 min mellan runs)
  → Jules payload (HEALING_FIX profile)
  → Jules remediation (google-labs-code/jules-action@v1.0.0)
  → Sensitive file guard (ARMORED check)
  → Commit + push fix
  → Retry limit (max 3 i 2 timmar, skapar GitHub issue vid överskridande)
  → Metrics artifact
```

### Safety Mechanisms

| Guard | Beskrivning |
|-------|------------|
| Cooldown | 30 min mellan self-healing runs per branch |
| Retry limit | Max 3 försök inom 2 timmar, sedan GitHub issue |
| ARMORED guard | Blockerar ändringar i `.github/workflows/`, `*auth*`, `*secret*`, `*token*` om `vars.JULES_ARMORED != 'true'` |
| Bot loop prevention | Commit-author check + `[skip-jules-review]` marker |

### self_heal_pr.yml (Manuell)

Samma healing-logik men triggas via:
- `workflow_dispatch` med PR-nummer
- `pull_request_target` med label `jules-heal`

Blockerar cross-repo PRs (säkerhet).

### classify_failure.py

Taxonomi-klassificering av CI-failures. Sparar `failure_classification.json` med taxonomy och failing_targets.

---

## 8. Deployment

### deploy.yml

Push till main → Azure Container Apps:

```
1. Azure login (OIDC — federated credentials)
2. ACR login
3. Docker build (Python 3.12-slim)
   → Tag: {ACR}.azurecr.io/sejfa:{sha} + :latest
4. Docker push (sha + latest)
5. Container Apps deploy (azure/container-apps-deploy-action@v2)
```

### Secrets

| Secret | Användning |
|--------|----------|
| AZURE_CLIENT_ID | OIDC federation |
| AZURE_TENANT_ID | OIDC federation |
| AZURE_SUBSCRIPTION_ID | OIDC federation |
| ACR_NAME | Container Registry |
| APP_NAME | Container App name |
| RESOURCE_GROUP | Azure resource group |
| JULES_API_KEY | Jules API (review + healing + health) |
| JIRA_API_TOKEN | Jira REST API |
| JIRA_USER_EMAIL | Jira auth |
| JIRA_URL | Jira base URL |

### post_deploy_verify.yml

Triggas av deploy completion (success):

```
1. Azure login (OIDC)
2. Hämta deployment info (FQDN + revision)
3. Health check med 5 retries (10s interval)
4. Om healthy:
   → Extrahera GE-XXX från commit message (|| true om saknas)
   → Kommentera Jira: "Deployed & Verified"
5. Om unhealthy:
   → Rollback: aktivera föregående revision, deaktivera current
   → Kommentera Jira: "Deploy failed — rolled back"
6. Step summary
```

Jira-steg hanterar commits utan GE-tag gracefully (skippar Jira-kommentar).

---

## 9. Branch Protection (main)

Konfigurerat per 2026-02-13:

| Setting | Value |
|---------|------|
| Require a pull request before merging | ✅ ON |
| Require approvals | ❌ OFF (solo dev, ingen reviewer) |
| Do not allow bypassing | ✅ ON |
| Required status checks | ci.yml (test + lint + security) |

### Self-Approval Limitation

GitHub blockerar self-approval med egna tokens. Eftersom Simon är ensam dev och det inte finns andra reviewers, är "Require approvals" avstängt. PRs behöver fortfarande passera CI.

---

## 10. Scripts

### jules_payload.py

Bygger kompakt JSON-payload för Jules. Två profiler:

| Profile | Användning |
|---------|----------|
| QUICK_REVIEW | jules_review.yml, jules_health_check.yml |
| HEALING_FIX | self_healing.yml, self_heal_pr.yml |

Output: `artifacts/jules_context.json` + `GITHUB_OUTPUT` variabler (files_changed_count, diff_bytes_sent, log_lines_sent).

### jules_review_api.py

REST-klient mot `jules.googleapis.com/v1alpha`. Flow:

```
1. derive_source_name(repo)  → "sources/github/{owner}/{repo}"
2. list_sources(api_key)     → verifiera att source finns
3. create_session(...)       → POST /v1alpha/sessions
4. poll_session(...)         → GET med polling (30s intervall, 18 försök = 9 min)
5. extract_review_text(...)  → Extrahera findings
6. format_review_body(...)   → Markdown-formatering
7. post_review_comment(...)  → gh CLI → PR comment
```

`automationMode` utelämnas medvetet för att förhindra att Jules skapar PRs.

### classify_failure.py

Analyserar CI-failure logs och kategoriserar:
- Taxonomy (test_failure, lint_failure, import_error, etc.)
- Failing targets (specifika testfiler/moduler)

### preflight.sh

Validerar prereqs: Python, pip, requirements installerade, git-status ren.

---

## 11. AI Agents

| Agent | Roll | Trust Level |
|-------|------|------------|
| **Claude Code** | Primary agent, kör Ralph Loop | ✅ Betrodd |
| **Jules (Google)** | Code review + self-healing | ✅ Betrodd (med guards) |
| **Codex (OpenAI)** | *Användes en gång* | ❌ INTE betrodd |

### Codex-Incidenten

PR #383: Codex markerade AC1-AC9 som klara utan att implementera dem. Reverterad i PR #384.

---

## 12. Memory System

Persistent kontext via `memory/` directory + `CLAUDE.md`:

```
CLAUDE.md                          # Root — snabbreferens
.claude/CLAUDE.md                  # Projektinstruktioner (Ralph)
memory/
├── context/
│   ├── architecture.md            # Loop flow, pipeline, hooks
│   └── known-issues.md            # Kända buggar (uppdateras löpande)
├── projects/
│   └── sejfa.md                   # Projektöversikt
└── people/                        # Personprofiler
```

---

## 13. API Endpoints

| Endpoint | Metod | Beskrivning |
|----------|-------|------------|
| `/` | GET | Root greeting (JSON) |
| `/health` | GET | Health check (deploy verification) |
| `/admin/login` | POST | Admin-inloggning |
| `/admin` | GET | Admin dashboard (auth) |
| `/admin/statistics` | GET | Statistik (auth) |
| `/admin/subscribers` | GET/POST | Lista/skapa subscribers (auth) |
| `/admin/subscribers/<id>` | GET/PUT/DELETE | Hantera subscriber (auth) |
| `/admin/subscribers/search` | GET | Sök subscribers (auth) |
| `/admin/subscribers/export` | GET | Exportera CSV (auth) |
| `/expenses/` | GET | Expense tracker |
| `/monitor` | GET | Real-time monitoring dashboard |

---

## 14. Remaining Issues

### Repo Hygiene

| Issue | Status |
|-------|-------|
| ~79 öppna PRs (mestadels Jules-genererade review-PRs) | Kräver `cleanup-branches.yml` dispatch |
| ~30+ stale branches | Samma cleanup workflow |

### Jules API Latency

Jules API:t kan fortfarande timeoutar (9 min polling), men detta blockerar inte längre merges. Review-kommentar postas med timeout-varning.

---

## 15. Historical Fixes (Resolved)

| Date | Issue | Fix |
|------|-------|----|
| 2026-02-13 | Jules 404 (`derive_source_name` hyphens → slashes) | Commit `5c97876` |
| 2026-02-13 | Post-deploy verify crash utan GE-tag | `|| true` fallback i grep |
| 2026-02-13 | Coverage scope mismatch (ci/ci_branch/finish-task) | Synkroniserat till `--cov=src --cov=app.py` |
| 2026-02-13 | Jules review saknade `synchronize` trigger | Lade till i workflow triggers |
| 2026-02-13 | Jules API failures blockerade merges | Return 0 på infra-failures, status alltid "success" |
| 2026-02-13 | Codex falska ACs (PR #383) | Reverterad i PR #384 |

---

## 16. Things NOT Part of the Loop

| Sak | Vad det är | Varför det INTE är del av loopen |
|-----|-----------|----------------------------------|
| Cockpit MCP | Docker MCP på dev-maskin | Används av Cowork, inte Ralph |
| Monitor | `ralph-monitor.pages.dev` | Cloudflare Pages dashboard, separat |
| `gruppett.fredlingautomation.dev` | EXISTERAR INTE | Referera aldrig till denna URL |
