# Task: GE-35 - Backend TEST (Expense Tracker)

## Status
- **Jira ID:** GE-35
- **Type:** Task
- **Priority:** Medium
- **Branch:** feature/GE-35-backend-test-expense-tracker
- **Status:** ✅ COMPLETE
- **PR:** https://github.com/itsimonfredlingjack/grupp-ett-github/pull/161

## Overview
Build ExpenseTracker backend using strict TDD and 3-layer architecture. Goal: log private expenses. Business logic must be clean from Flask using dependency injection.

## Domain Model: Expense Entity
- `id: int`
- `title: str`
- `amount: float`
- `category: str`

Service: `ExpenseService` handles the logic.

## Business Rules (Unit Tests Required in app/business/)

1. **amount** must be > 0 (cannot log negative expenses)
2. **title** cannot be empty
3. **category** must be one of: "Mat", "Transport", "Boende", "Övrigt"
   - Invalid category → raise error (for now)

## Technical Requirements

### Language Convention
- **Code/Comments:** English
- **UI/Error Messages:** Swedish

### Database
- `sqlite:///:memory:` (InMemoryRepository for this sprint)

### Architecture (Strict 3-Layer)
1. **Data Layer:** `InMemoryExpenseRepository` (implements abstract protocol)
2. **Business Layer:** `ExpenseService` (pure Python, NO Flask imports!)
   - Receives repository via `__init__` (Dependency Injection)
3. **Presentation Layer:** Flask Blueprint
   - `routes.py` handles HTTP, calls service

### Routes
- `GET /` – List all expenses
- `POST /add` – Form to add new expense
- `GET /summary` – Simple page showing total amount

## Acceptance Criteria (Definition of Done)

- [x] Project structure set up per Clean Architecture (data/business/presentation)
- [x] Unit tests (pytest) GREEN for all business rules above
- [x] Integration tests verify routes return 200 OK and render correct template
- [x] Dependency Injection works via `create_app` factory
- [x] `ruff check .` passes without warnings
- [x] Changes committed and pushed
- [x] PR created

## Iteration Log

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Setup project structure | ✅ | 3-layer architecture in place (data/business/presentation) |
| 2 | Write business rule tests | ✅ | 16 unit tests passing (validation rules) |
| 3 | Implement ExpenseService | ✅ | Service with DI, validates all rules |
| 4 | Write integration tests | ✅ | 19 integration tests (routes, templates) |
| 5 | Implement Flask routes | ✅ | Blueprint with GET /, POST /add, GET /summary |
| 6 | Verify all tests pass | ✅ | 35/35 tests passing (16 unit + 19 integration) |
| 7 | Lint and format | ✅ | ruff check passed (no warnings) |
| 8 | Commit and push | ✅ | PR created: #161 |

## Failed Attempts
(None yet)

## Notes
- Strict TDD: red → green → refactor
- No Flask in business layer
- Use type hints for all functions
- Docstrings for public functions (Google-style)
