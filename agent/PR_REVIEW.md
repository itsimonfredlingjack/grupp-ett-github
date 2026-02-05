## High Severity

### 1. Missing CSRF Protection in Forms (Security)
The `POST /add` route in `src/expense_tracker/presentation/routes.py` and the form in `src/expense_tracker/templates/expense_tracker/index.html` lack CSRF protection. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Action:** Implement `Flask-WTF` or manually handle CSRF tokens.

## Medium Severity

### 2. Hardcoded Secret Key (Security)
`app.py` uses a hardcoded `secret_key` ("dev-secret-key"). While acceptable for local development, this poses a security risk if the code is deployed to a production environment without override.
**Action:** Load `SECRET_KEY` from environment variables.

### 3. Requirement Deviation: Database Implementation (Correctness)
The task requirements explicitly specify `DB: sqlite:///:memory:`. The current implementation uses a Python `list` in `InMemoryExpenseRepository`. This deviates from the requirement and misses the opportunity to verify SQL compatibility.
**Action:** Replace the list-based implementation with an SQLite-based implementation.

## Low Severity

### 4. Debug Mode Enabled in Main (Reliability)
`app.py` enables `debug=True` in the `__main__` block. This exposes the debugger if the application is run directly in a production environment.
**Action:** Use an environment variable to toggle debug mode or disable it by default.

### 5. In-Memory Data Storage (Reliability)
`InMemoryExpenseRepository` stores data in a list (or in-memory DB), which causes data loss upon application restart. This is expected for MVP but limits utility.
**Action:** Plan for persistent storage (e.g., SQLite file or PostgreSQL) in the next iteration.

### 6. Test Configuration Duplication (Maintainability)
`tests/expense_tracker/test_routes.py` manually constructs the Flask app for testing instead of using the `create_app` factory or a consistent fixture. This risks configuration drift between tests and production.
**Action:** Refactor tests to use `create_app` or a shared `conftest.py` fixture.
