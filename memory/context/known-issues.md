# Known Issues

Verifierade problem per 2026-02-13.

## Aktiva buggar

### 1. Post-Deploy Verify kraschar utan GE-tag
- **Fil:** `.github/workflows/post_deploy_verify.yml` rad 66-72
- **Symptom:** "Extract Jira ticket from commit" step failar
- **Orsak:** `grep -oP 'GE-\d+'` hittar ingen match → steg kraschar
- **Impact:** Falsk failure-alert. Deployen fungerar, men verifieringen rapporterar fail.
- **Bevis:** Run 21986294324 (2026-02-13 12:08) — health check passerade, Jira-extraktion kraschade
- **6 av 10 senaste commits på main saknar GE-tag**
- **Fix:** Gör Jira-steget continue-on-error eller bättre felhantering

### 2. Jules Review API failar
- **Fil:** `scripts/jules_review_api.py` (via `.github/workflows/jules_review.yml`)
- **Symptom:** "Call Jules API and post review" step failar
- **Orsak:** Okänd — 404-buggen (derive_source_name) fixades i commit 5c97876, men API:t failar fortfarande
- **Möjliga orsaker:** Expired API key, rate limit, annan API-endpoint-bugg
- **Impact:** Ingen AI-review på nya PRs
- **Bevis:** 2 av 3 senaste Jules Review runs failade (PR #387 och itsimonfredlingjack-patch)

### 3. Coverage-scope mismatch
- **Filer:** `.claude/skills/finish-task/SKILL.md` vs `.github/workflows/ci.yml` vs `.github/workflows/ci_branch.yml`
- **Symptom:** Lokal quality gate kan faila medan CI passerar, eller tvärtom
- **Detaljer:**
  - finish-task: `--cov=.` (all kod)
  - ci.yml: `--cov=src` (bara src/)
  - ci_branch.yml: `--cov=src --cov=app.py` (src/ + app.py)
- **Fix:** Synkronisera alla tre till samma scope

### 4. Jules review triggar inte på synchronize
- **Fil:** `.github/workflows/jules_review.yml`
- **Symptom:** Extra commits efter PR-skapande ger ingen ny Jules review
- **Orsak:** Workflow triggers: `opened`, `ready_for_review` — saknar `synchronize`
- **Impact:** Låg — agenten pushar normalt bara en gång före PR

## Historiska problem (lösta)

### Jules 404 — LÖST
- **Commit:** 5c97876
- **Orsak:** `derive_source_name()` genererade `sources/github-{owner}-{name}` (hyphens) istället för `sources/github/{owner}/{name}` (slashes)

### Codex falska ACs — LÖST
- **PR #383:** Codex markerade AC1-AC9 som klara (falskt)
- **PR #384:** Reverterad

## Repo-hygien

- **79 öppna PRs** — de flesta Jules-genererade review-PRs från 11 feb
- **30+ stale branches** — gamla feature branches som aldrig städades
- `cleanup-branches.yml` finns men kräver manuell trigger med "DELETE ALL BRANCHES"
