## High Severity

### 1. Missing CSRF Protection in Forms (Security)
The `POST /add` route in `src/expense_tracker/presentation/routes.py` and the form in `src/expense_tracker/templates/expense_tracker/index.html` lack CSRF protection. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Action:** Implement `Flask-WTF` or manually handle CSRF tokens.

## Medium Severity

### 2. Requirement Deviation: Database Implementation (Correctness)
The task requirements explicitly specify `DB: sqlite:///:memory:`. The current implementation in `src/expense_tracker/data/repository.py` uses a Python `list`. This deviates from the requirement.
**Action:** Replace the list-based implementation with an SQLite-based implementation.

### 3. Integration Tests Bypass App Factory (Reliability)
`tests/expense_tracker/test_routes.py` manually constructs the Flask app instance instead of using the `create_app()` factory. This risks drift between test and production environments.
**Action:** Refactor tests to use `create_app` or a shared fixture that mimics production setup.

### 4. Blueprint Registration Path Mismatch (Correctness)
Integration tests register the blueprint at `/`, while `app.py` registers it at `/expenses`. This discrepancy could mask path-related issues.
**Action:** Register the blueprint at `/expenses` in tests to match production.

## Low Severity

### 5. Debug Mode Enabled in Main (Reliability)
`app.py` enables `debug=True` in the `__main__` block. This exposes the debugger if the application is run directly in a production environment.
**Action:** Use an environment variable to toggle debug mode.
