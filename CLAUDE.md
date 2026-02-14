# Memory

## Me
Simon Fredling Jack, AI Automation Architect. Bygger websites, applikationer, local LLMs, n8n workflows, RAG pipelines.

## People
| Who | Role |
|-----|------|
| **Simon** | Projektägare, AI Automation Architect |
| **Jules** | Google Jules AI — code review + self-healing |
| **Codex** | OpenAI Codex — INTE BETRODD (förstörde PR #383) |
→ Profiler: memory/people/

## Terms
| Term | Meaning |
|------|--------|
| Ralph / Ralph Loop | Agentic dev loop — Claude Code kör TDD lokalt |
| GE-XXX | Jira ticket ID (Grupp Ett) |
| AC | Acceptance Criteria |
| stop-hook | Hook som blockerar exit tills DONE |
| prevent-push | Hook som blockerar push med no-push markers |
| finish-task | Skill: auto-merge+deploy flow |
| start-task | Skill: hämta Jira, skapa branch, starta loop |
| self-healing | GitHub Action: auto-fix CI failures via Jules |
| cockpit MCP | Docker MCP — INTE del av loopen |
| monitor | ralph-monitor.pages.dev — INTE del av loopen |
→ Full glossary: memory/glossary.md

## Projects
| Name | What |
|------|------|
| **SEJFA** | Flask-app + agentic DevOps loop |
| **Blueprint 2026** | Systemdokumentation (`docs/BLUEPRINT_SEJFA_2026.md`) |
→ Detaljer: memory/projects/

## Preferences
- Svenska, men tänk på engelska. Engelska termer ok.
- Challenge assumptions
- Action > clarification vid låg risk
- Production-ready, typed, functional patterns
- Minimal comments
- ALDRIG: falska statusrapporter, irrelevanta tangenter, nämna saker han inte frågat om

## Known Issues (2026-02-14)
Alla tidigare kända buggar (post-deploy verify, Jules API, coverage scope, synchronize trigger) är lösta.
Se `docs/BLUEPRINT_SEJFA_2026.md` Section 15 för historik.
→ Detaljer: memory/context/known-issues.md

## Architecture Quick Ref
→ memory/context/architecture.md
