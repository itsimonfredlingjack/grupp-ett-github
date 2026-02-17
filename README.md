<div align="center">

# SEJFA

### Secure Enterprise Jira Flask Agent

**From Jira Ticket to Production — Untouched by Human Hands.**

[![Python](https://img.shields.io/badge/Python-3.10_%7C_3.11_%7C_3.12_%7C_3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Azure](https://img.shields.io/badge/Azure-Container%20Apps-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![Jira](https://img.shields.io/badge/Jira-Cloud%20API-0052CC?style=for-the-badge&logo=jira&logoColor=white)](https://www.atlassian.com/software/jira)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

[![Tests](https://img.shields.io/badge/Tests-370%2B-brightgreen?style=flat-square&logo=pytest&logoColor=white)](#test-suite)
[![Coverage](https://img.shields.io/badge/Coverage-80%25%2B-brightgreen?style=flat-square&logo=codecov&logoColor=white)](#test-suite)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

---

*An autonomous DevOps loop system where AI agents own the entire lifecycle — from Jira ticket to production deployment — powered by Claude Code and the Ralph Loop.*

[Getting Started](#getting-started) · [Architecture](#architecture) · [API Reference](#api-reference) · [Documentation](#documentation)

</div>

---

## What is SEJFA?

SEJFA is an **Agentic DevOps Loop System** built by **Filippa, Simon, Jonas O, Emma, and Annika**. It demonstrates a fully autonomous software development workflow where an AI agent (powered by **Claude Code**) picks up Jira tickets, writes tests, implements features, passes quality gates, creates pull requests, and triggers deployment to Azure — all without manual intervention.

The system is built on a clean 3-layer Flask architecture and includes a newsletter subscription service, an expense tracker, admin management, and real-time agent monitoring.

### Why SEJFA?

| Problem | SEJFA's Solution |
|:--------|:-----------------|
| Manual ticket-to-code workflow | Autonomous Jira-to-PR pipeline via agent skills |
| Inconsistent code quality | Enforced TDD cycle with automated quality gates |
| Slow feedback loops | Real-time monitoring dashboard for agent activity |
| Risky deployments | SHA-tagged Docker images with CI/CD and health checks |

---

## The Ralph Loop

The **Ralph Loop** is the core engine that drives autonomous development. It enforces a strict **Test-Driven Development** cycle that every task must pass before reaching production.

```
   +-------+       +-------+       +----------+       +--------+
   |  RED  | ----> | GREEN | ----> | REFACTOR | ----> | VERIFY |
   | Write |       | Pass  |       | Optimize |       | Lint + |
   | Test  |       | Test  |       | Code     |       | Test   |
   +-------+       +-------+       +----------+       +--------+
       ^                                                   |
       |                                                   |
       +------- Loop until all criteria met <--------------+
```

### Quality Gates (Stop-Hook)

Before any task can be marked complete, the stop-hook enforces:

- **pytest** — All tests must pass (370+ test suite)
- **ruff check** — Zero linting warnings allowed
- **ruff format** — Code must be properly formatted
- **UI scope guard** — UI tickets must modify the correct Flask templates
- **PR merge gate** — Blocks until PR is merged or auto-merge is enabled
- **Max iterations** — Auto-creates a WIP draft PR after 25 iterations

---

## Architecture

SEJFA follows a **clean 3-layer architecture** with dependency injection across all modules:

```
 Presentation (Flask Blueprints + Templates)
         |
   Business Logic (Services with validation)
         |
     Data Layer (Models + Repositories)
```

Every module — Newsflash, Expense Tracker, Admin, Monitor — follows this pattern. Services receive their repositories via constructor injection, keeping layers decoupled and testable.

```mermaid
graph TD
    PO[Product Owner] -->|Creates Ticket| Jira[Jira Cloud]
    Jira -->|/start-task| Agent[Claude Code Agent]

    subgraph "The Ralph Loop"
        Agent -->|1. Write failing test| Red[Red]
        Red -->|2. Implement code| Green[Green]
        Green -->|3. Optimize| Refactor[Refactor]
        Refactor -->|4. Lint + Test| Verify[Verify]
        Verify -->|Fail| Red
    end

    Verify -->|Pass| Finish[/finish-task]
    Finish -->|Push + PR| GH[GitHub]
    GH -->|CI Pipeline| CI[GitHub Actions]
    CI -->|Test + Lint + Security| Gate{Pass?}
    Gate -->|Yes| Merge[Merge to main]
    Gate -->|No| Agent
    Merge -->|deploy.yml| ACR[Azure Container Registry]
    ACR -->|Deploy| ACA[Azure Container Apps]
    ACA -->|Live| Prod[gruppett.fredlingautomation.dev]
```

---

## Key Features

### Agentic Workflow

| Skill | Description |
|:------|:------------|
| `/start-task` | Fetches Jira ticket, creates feature branch, initializes `CURRENT_TASK.md` with context |
| `/finish-task` | Verifies quality, commits, pushes, creates PR, and updates Jira status |
| `/preflight` | Validates the system is ready for a new task |

### Application Modules

| Module | Description |
|:-------|:------------|
| **Newsflash** | Newsletter subscription service with email validation, subscriber management, and a public-facing landing page |
| **Expense Tracker** | Track and categorize expenses with summary views, built on clean 3-layer architecture |
| **Admin Panel** | Token-based authentication, subscriber CRUD, statistics dashboard, search, and CSV export |
| **Monitor** | Real-time WebSocket dashboard tracking agent loop iterations, status, and performance |
| **Jira Integration** | Full REST client — ticket fetching, JQL search, comments (Atlassian Document Format), status transitions, sub-task creation |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker** (optional, for container testing)
- **Jira Account** with API token (for agent integration)
- **Azure Account** (for deployment)

### Installation

```bash
# Clone the repository
gh repo clone itsimonfredlingjack/grupp-ett-github
cd grupp-ett-github

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///newsflash.db
JIRA_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

### Run Tests

```bash
source venv/bin/activate && pytest -xvs
```

### Run Linting

```bash
source venv/bin/activate && ruff check .
```

---

## CI/CD Pipeline

The CI/CD pipeline ensures no code reaches production without passing rigorous quality controls.

### Continuous Integration

Triggered on every push to `main` and on pull requests. Tests run across **4 Python versions** in parallel:

| Job | What it does | Gate |
|:----|:-------------|:-----|
| **Test** | `pytest` with coverage report | 80% minimum coverage |
| **Lint** | `ruff check` + `ruff format` | Zero warnings |
| **Security** | `safety check` | Reports vulnerabilities |

Coverage is uploaded to **Codecov** for the Python 3.12 run.

### Continuous Deployment

On merge to `main`:

1. Authenticate to Azure via **OIDC** (no stored passwords)
2. Build Docker image tagged with **git SHA** for traceability
3. Push image to **Azure Container Registry**
4. Deploy to **Azure Container Apps**

Every deployment is traceable via the `/version` endpoint which returns the current git SHA.

---

## API Reference

<details>
<summary><strong>Public Endpoints</strong></summary>

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/` | GET | Landing page (Newsflash) |
| `/subscribe` | POST | Register a subscriber |
| `/thank-you` | GET | Confirmation page |
| `/api` | GET | API greeting |
| `/health` | GET | Health check with timestamp |
| `/version` | GET | Deployed git SHA |
| `/expenses/` | GET | Expense tracker |
| `/expenses/summary` | GET | Expense summary |

</details>

<details>
<summary><strong>Admin Endpoints (Token Required)</strong></summary>

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/admin/login` | POST | Admin login (returns JWT) |
| `/admin` | GET | Admin dashboard |
| `/admin/statistics` | GET | Subscriber statistics |
| `/admin/subscribers` | GET | List all subscribers |
| `/admin/subscribers` | POST | Create subscriber |
| `/admin/subscribers/<id>` | GET | Get subscriber |
| `/admin/subscribers/<id>` | PUT | Update subscriber |
| `/admin/subscribers/<id>` | DELETE | Delete subscriber |
| `/admin/subscribers/search` | GET | Search subscribers |
| `/admin/subscribers/export` | GET | Export CSV |

</details>

<details>
<summary><strong>Monitor Endpoints</strong></summary>

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/api/monitor/state` | GET | Get monitor state |
| `/api/monitor/state` | POST | Update monitor state |
| `/api/monitor/reset` | POST | Reset monitor |

</details>

---

## Test Suite

SEJFA has a comprehensive test suite with **370+ tests** covering all modules.

| Test Directory | Coverage | Test Files |
|:---------------|:---------|:-----------|
| `tests/agent/` | Ralph Loop, stop-hook, prevent-push | 5 |
| `tests/core/` | Admin auth, subscriber management, statistics | 5 |
| `tests/expense_tracker/` | ExpenseService, repository, routes | 3 |
| `tests/integrations/` | Jira client, Jules review system | 4 |
| `tests/newsflash/` | Subscription flow, validation, data layer | 5 |
| `tests/utils/` | Health check, security | 2 |

### Test Markers

```python
@pytest.mark.unit          # Isolated unit tests
@pytest.mark.integration   # Tests with database dependencies
@pytest.mark.e2e           # End-to-end workflow tests
@pytest.mark.slow          # Long-running tests (excluded in quick runs)
```

### Code Quality Tools

| Tool | Purpose | Config |
|:-----|:--------|:-------|
| **Ruff** | Linting & formatting | 88 chars/line, Python 3.10 target |
| **pytest-cov** | Code coverage | 80% minimum, branch coverage |
| **safety** | Dependency vulnerabilities | Reports in CI |
| **Codecov** | Coverage tracking | Published on Python 3.12 |

---

## Deployment

### Docker

The application is containerized using **Python 3.12-slim** with **Gunicorn** (4 workers) on port 5000. The container runs as a non-root user (`appuser`) and includes a built-in health check.

```bash
# Build
docker build --build-arg GIT_SHA=$(git rev-parse HEAD) -t sejfa .

# Run
docker run -p 5000:5000 sejfa
```

### Azure Container Apps

Production is hosted on **Azure Container Apps** with automatic scaling. Images are stored in **Azure Container Registry** and deployments are managed via **GitHub Actions** with OIDC authentication. The application is accessible via **Cloudflare Tunnel** at [gruppett.fredlingautomation.dev](https://gruppett.fredlingautomation.dev).

---

## Project Structure

```
grupp-ett-github/
├── app.py                          # Flask entry point (create_app factory)
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Ruff, pytest, coverage config
├── Dockerfile                      # Production image (Python 3.12-slim)
│
├── src/
│   ├── sejfa/                      # Main package
│   │   ├── core/                   # Admin auth, subscriber service
│   │   ├── integrations/           # Jira API client
│   │   ├── monitor/                # Real-time monitoring (WebSocket)
│   │   ├── newsflash/              # Newsletter subscription module
│   │   │   ├── data/               # Models + repository
│   │   │   ├── business/           # Subscription service
│   │   │   └── presentation/       # Blueprint + templates
│   │   └── utils/                  # Health check, security
│   └── expense_tracker/            # Expense tracking module
│       ├── data/                   # Expense model + repository
│       ├── business/               # ExpenseService
│       └── presentation/           # Blueprint + templates
│
├── tests/                          # Test suite (370+ tests)
├── .claude/                        # Agent configuration
│   ├── hooks/                      # Quality gate hooks
│   └── skills/                     # Agent skills (start-task, finish-task)
├── .github/workflows/              # CI/CD pipelines
└── docs/                           # Documentation
```

---

## Agentic Development Guide

### Complete Workflow

| Step | Component | What Happens |
|:-----|:----------|:-------------|
| 1 | **Jira** | Product owner creates a ticket with requirements and acceptance criteria |
| 2 | **`/start-task`** | Agent fetches ticket, creates feature branch, initializes `CURRENT_TASK.md` |
| 3 | **Ralph Loop** | TDD cycle: Red -> Green -> Refactor -> Verify (repeats until all criteria met) |
| 4 | **Stop-Hook** | Quality gate validates pytest, ruff, and UI scope — blocks if anything fails |
| 5 | **`/finish-task`** | Agent commits, pushes, and creates a pull request |
| 6 | **GitHub Actions** | Automated tests, linting, and security scanning across 4 Python versions |
| 7 | **Deploy** | On merge to main: Docker build and deploy to Azure Container Apps |
| 8 | **Production** | Application is live at `gruppett.fredlingautomation.dev` |

### Using the Agent

```bash
# Start a new task from Jira
claude /start-task GE-123

# The agent enters the Ralph Loop automatically
# Red -> Green -> Refactor -> Verify

# Finish the task when all criteria are met
claude /finish-task
```

---

## Documentation

- **[Full Project Documentation](docs/FINAL_DOCUMENTATION.md)** — Architecture, APIs, pipelines, and deployment
- **[Jules Playbook](docs/jules-playbook.md)** — AI review system insights

---

## Contributing

1. Fork the repository
2. Create a feature branch (`feature/GE-XXX-description`)
3. Follow the Ralph Loop methodology (write tests first)
4. Ensure all tests pass and linting is clean
5. Submit a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built by the SEJFA Team — Filippa, Simon, Jonas O, Emma & Annika*

</div>
