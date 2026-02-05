## Critical Severity

### 1. Implementation Deviates from Requirements (Correctness)
The `CURRENT_TASK.md` requirements explicitly specify `DB: sqlite:///:memory:`. However, `src/expense_tracker/data/repository.py` implements storage using a Python `list`. This deviation affects data persistence behavior and does not match the approved design.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database as required.

## High Severity

### 2. Missing CSRF Protection (Security)
The `POST /add` route in `src/expense_tracker/presentation/routes.py` and the corresponding form lack CSRF protection. Furthermore, `tests/expense_tracker/test_routes.py` explicitly disables CSRF (`WTF_CSRF_ENABLED = False`). This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Implement CSRF protection using `Flask-WTF` and enable it in tests.

## Medium Severity

### 3. Tests Bypass Application Factory (Reliability)
`tests/expense_tracker/test_routes.py` manually constructs a Flask application and wires dependencies, bypassing the `create_app` factory in `app.py`. This means the actual production wiring is not verified by integration tests, potentially leading to configuration drift.
**Action:** Refactor tests to use `create_app` or a shared fixture that accurately reflects production configuration.

## Low Severity

### 4. Debug Mode Enabled in Production Entrypoint (Security)
`app.py` enables `debug=True` in the `__main__` block. While this is convenient for development, it poses a security risk if the container entrypoint invokes this file directly in a production environment.
**Action:** Configure debug mode via environment variables (e.g., `FLASK_DEBUG`).
