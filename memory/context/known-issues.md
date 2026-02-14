# Known Issues

Senast uppdaterad: 2026-02-14

## Aktiva problem

### Repo-hygien
- **~79 öppna PRs** — mestadels Jules-genererade review-PRs från 11 feb
- **~30+ stale branches** — gamla feature branches som aldrig städades
- `cleanup-branches.yml` finns men kräver manuell trigger med "DELETE ALL BRANCHES"

### Jules API Latency
- Jules API:t kan fortfarande timeoutar (9 min polling)
- Blockerar INTE merges (return 0 + status "success")
- Review-kommentar postas med timeout-varning

---

## Historiska problem (alla lösta 2026-02-13)

### 1. Post-Deploy Verify kraschade utan GE-tag — LÖST
- **Fil:** `.github/workflows/post_deploy_verify.yml`
- **Orsak:** `grep -oP 'GE-\d+'` utan match kraschade steget
- **Fix:** Lade till `|| true` fallback (commit `d1dee71`)

### 2. Jules Review API failade — LÖST
- **Fil:** `scripts/jules_review_api.py` + `jules_review.yml`
- **Orsak:** 404 (derive_source_name hyphens → slashes) + infra-failures blockerade merges
- **Fix:** Commit `5c97876` (404) + return 0 på infra-failures + status alltid "success" (PR #386)

### 3. Coverage-scope mismatch — LÖST
- **Filer:** ci.yml, ci_branch.yml, finish-task/SKILL.md
- **Orsak:** Tre olika scopes (`--cov=.` vs `--cov=src` vs `--cov=src --cov=app.py`)
- **Fix:** Synkroniserat till `--cov=src --cov=app.py` (commit `d1dee71`)

### 4. Jules review triggade inte på synchronize — LÖST
- **Fil:** `.github/workflows/jules_review.yml`
- **Orsak:** Saknades `synchronize` i trigger types
- **Fix:** Lade till `synchronize` (commit `d1dee71`)

### 5. Jules 404 — LÖST
- **Commit:** `5c97876`
- **Orsak:** `derive_source_name()` genererade hyphens istället för slashes

### 6. Codex falska ACs — LÖST
- **PR #383:** Codex markerade AC1-AC9 som klara (falskt)
- **PR #384:** Reverterad
