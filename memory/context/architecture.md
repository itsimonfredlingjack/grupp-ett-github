# SEJFA Architecture

## Loop Flow (Ralph Wiggum Loop)

Kör LOKALT på Simons dev-maskin via Claude Code.

```
Jira ticket
  → /start-task (preflight, branch, CURRENT_TASK.md)
  → TDD-cykel (test → fail → implement → pass → refactor)
  → /finish-task:
      1. pytest -xvs --cov=. --cov-fail-under=80
      2. ruff check . && ruff format --check .
      3. git add -A && git commit
      4. git push -u origin {branch}
      5. gh pr create
      6. gh pr checks --watch  (väntar på ci.yml)
      7. gh pr merge --squash
      8. Jira → Done
      9. <promise>DONE</promise>
```

## GitHub Actions Pipeline

```
Push till feature-branch
  → ci_branch.yml (test matrix: 3.10-3.13 + lint + security)

PR mot main
  → ci.yml (required check — gh pr checks väntar på denna)
  → jules_review.yml (AI code review via Jules API)

Merge till main
  → deploy.yml (Azure OIDC → ACR build → Container Apps deploy)
  → post_deploy_verify.yml (health check → Jira comment eller rollback)

CI failure
  → self_healing.yml (Jules auto-fix, max 3 retries, 30-min cooldown)
```

## Lokala Git-kommandon i loopen

| Steg | Kommando |
|------|----------|
| Pre-flight | `git status --porcelain` |
| Verifiera branch | `git branch --show-current` |
| Synka | `git checkout main && git pull origin main` |
| Ny branch | `git checkout -b feature/GE-XXX-slug` |
| Commit | `git add -A && git commit -m "GE-XXX: ..."` |
| Push | `git push -u origin {branch}` |
| Skapa PR | `gh pr create --title "..." --body "..."` |
| Vänta CI | `gh pr checks "$PR_URL" --watch` |
| Merge | `gh pr merge --squash "$PR_URL"` |

## Hooks

| Hook | Fil | Funktion |
|------|-----|----------|
| stop-hook | .claude/hooks/stop-hook.py | Blockerar exit tills `<promise>DONE</promise>` + quality gates |
| prevent-push | .claude/hooks/prevent-push.py | Blockerar push om CURRENT_TASK.md har no-push markers |

## 3-Layer Architecture (Flask-appen)

```
Data       → Modeller (dataclass) + Repository (in-memory)
Business   → Service med validering (INGEN Flask)
Presentation → Blueprint + templates
```

Dependency injection: Services får repository via `__init__`.

## Deployment

- **Target:** Azure Container Apps
- **Image:** Python 3.12-slim (Dockerfile)
- **Auth:** Azure OIDC (federated credentials)
- **Registry:** Azure Container Registry
- **Health:** /health endpoint

## INTE del av loopen

| Sak | Vad det är | Varför det INTE är del av loopen |
|-----|-----------|----------------------------------|
| Cockpit MCP | Docker MCP på dev-maskin | Används av Cowork, inte Ralph |
| Monitor | ralph-monitor.pages.dev | Cloudflare Pages dashboard, separat |
| gruppett.fredlingautomation.dev | EXISTERAR INTE | Referera aldrig till denna URL |
