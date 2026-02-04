# GE-31: Nyhetsbrevet Cursor The Mad

## Task Summary

Build a Flask application following strict 3-layer architecture with TDD (Test-Driven Development).

**Priority:** 1. Tests (red → green). 2. Minimal implementation.

---

## Configuration

| Variable | Value |
| :--- | :--- |
| **App Name** | `Nyhetsbrevet Cursor The Mad` |
| **Model** | `Website for newsletters` (FINANCE theme) |
| **Fields** | `three top news with headlines` (id:int, title:str, content:str) |
| **Business Rules** | 1. Headlines must be > 3 characters. 2. Max 10 news items per page. |
| **Routes** | `GET /`, `POST /add`, `GET /delete/<id>` |

---

## Rules & Setup

- **Language:** Code/Comments in **English**. UI/Error messages in **Swedish**.
- **Database:** `sqlite:///:memory:` for tests.
- **Dependency Injection:** REQUIRED. Service takes repository in `__init__`.

---

## Architecture (LOCKED)

### 1. Application Factory
- `create_app(config)` in `app/__init__.py`

### 2. Layer 1: Data (`app/data/`)
- Model (Dataclass/SQLAlchemy)
- Repository protocol (Abstract Base Class)
- `InMemoryRepository` (for tests/MVP)

### 3. Layer 2: Business (`app/business/`)
- Pure Python class (Service)
- **NEVER** depends on Flask or HTTP
- Repository injected in constructor

### 4. Layer 3: Presentation (`app/presentation/`)
- Flask Blueprint
- Handles HTTP (request/response), Templates, Forms
- Service injected via `app.config` or factory pattern

---

## Acceptance Criteria

### Phase 1: Core & Business Logic (Unit Tests)
- [x] Project structure created
- [x] Repository protocol + `InMemoryRepository` created
- [x] **TEST:** Unit tests (pytest) verify all business rules without Flask

### Phase 2: Integration & Web (Integration Tests)
- [x] `create_app` configures Flask and injects dependencies
- [x] Templates (`base.html` + pages) created with Swedish text
- [x] Routes implemented in Blueprint
- [x] **TEST:** Integration tests verify flows and HTTP status codes
- [x] `pytest` runs green. `ruff check .` passes

---

## Progress

### Iteration Table

| Iteration | Task | Status | Notes |
|-----------|------|--------|-------|
| 1 | Set up project structure and repository layer | ✅ DONE | Models, repository protocol, InMemoryRepository implemented |
| 2 | Create business service and unit tests | ✅ DONE | NewsService with business rules, 10 unit tests all passing |
| 3 | Create Flask app factory and integration tests | ✅ DONE | Flask app factory, routes, 10 integration tests all passing |
| 4 | Implement routes and templates | ✅ DONE | GET /, POST /add, GET /delete/<id> with Swedish templates |
| 5 | Final testing and linting | ✅ DONE | 20/20 tests pass, ruff check clean |

---

## Failed Attempts

(none yet)

---

## Next Step

1. Read this file
2. Create project structure
3. Implement repository protocol and InMemoryRepository
4. Write unit tests for business logic
5. Start TDD cycle

---

## Branch

`feature/GE-31-nyhetsbrevet-cursor-the-mad`

## Jira Ticket

GE-31: Nyhetsbrevet Cursor The Mad
