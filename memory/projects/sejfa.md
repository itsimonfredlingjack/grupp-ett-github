# SEJFA — Secure Enterprise Jira Flask Agent

**Repo:** itsimonfredlingjack/grupp-ett-github
**Branch:** main
**Status:** Aktiv, men med kända buggar i pipeline

## Vad det är
Flask-applikation med agentic DevOps-loop (Ralph Wiggum Loop).
Admin dashboard, subscriber management, expense tracker, real-time monitor.

## Deployment
- Azure Container Apps (deploy.yml → ACR → Container Apps)
- Post-deploy verification med auto-rollback

## Agentic Loop
- Kör lokalt via Claude Code på Simons maskin
- Skills: /start-task, /finish-task
- Hooks: stop-hook.py (quality gate), prevent-push.py
- Jira-integration: direkt REST API (src/sejfa/integrations/jira_client.py)

## AI Agents
- **Jules (Google):** Code review via API + self-healing via GitHub Action
- **Codex (OpenAI):** Användes, förstörde PR #383 — inte betrodd
- **Claude Code:** Kör Ralph Loop — primary agent

## Test
- 318+ tester, pytest
- Coverage: 80% minimum
- Python 3.10-3.13 matrix
- Ruff linting (E, F, W, I, N, UP, B, C4)

## Kända problem
Se memory/context/known-issues.md
