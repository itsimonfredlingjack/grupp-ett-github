# Glossary

SEJFA-projektets interna språk, förkortningar och termer.

## Acronyms
| Term | Meaning | Context |
|------|---------|---------|
| SEJFA | Secure Enterprise Jira Flask Agent | Projektnamnet |
| GE-XXX | Grupp Ett ticket ID | Jira-format, används i commits och branches |
| AC | Acceptance Criteria | Krav i Jira-tickets |
| TDD | Test-Driven Development | Loopens arbetsmetod |
| PR | Pull Request | GitHub PRs mot main |
| CI | Continuous Integration | GitHub Actions ci.yml |
| ACR | Azure Container Registry | Docker image storage |
| OIDC | OpenID Connect | Azure auth i deploy pipeline |
| FQDN | Fully Qualified Domain Name | Azure Container Apps URL |

## Internal Terms
| Term | Meaning |
|------|---------|
| Ralph / Ralph Loop / Ralph Wiggum Loop | Agentic dev loop — Claude Code kör TDD-cykeln lokalt |
| stop-hook | .claude/hooks/stop-hook.py — blockerar exit tills DONE |
| prevent-push | .claude/hooks/prevent-push.py — blockerar push med no-push markers |
| finish-task | .claude/skills/finish-task — auto-merge+deploy flow |
| start-task | .claude/skills/start-task — hämta Jira, skapa branch, starta loop |
| preflight | Validering att systemet är redo för ny uppgift |
| self-healing | GitHub Action som auto-fixar CI failures via Jules |
| Jules | Google Jules AI — code review + auto-fix agent |
| Codex | OpenAI Codex — extern agent som förstörde PR #383 (GE-59) |
| cockpit MCP | Docker-baserad MCP på dev-maskin — INTE del av loopen |
| monitor | ralph-monitor.pages.dev — Cloudflare Pages dashboard, INTE del av loopen |

## Infrastruktur
| Term | Meaning |
|------|---------|
| ai-server | RTX 4070 headless server |
| ai-server-2 | RTX 2060 headless server |
| dev-maskin | Simons laptop — här körs Ralph Loop |
| Azure Container Apps | Production deployment target |

## Projekt-codenames
| Codename | Project |
|----------|---------|
| SEJFA | Hela Flask-appen + agentic loop |
| Blueprint 2026 | Systemdokumentation (PR #387) |

## Nicknames → Full Names
| Nickname | Person/Thing |
|----------|-------------|
| Ralph | Ralph Wiggum Loop (agentic dev loop) |
| Jules | Google Jules AI |
| Codex | OpenAI Codex agent |
