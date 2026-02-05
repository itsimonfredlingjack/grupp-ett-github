# PR Review Findings

## High Severity

### 1. Missing CSRF Protection (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Action:** Implement CSRF protection using `Flask-WTF` or manual token verification for all state-changing endpoints.

### 2. Hardcoded Secret Key (Security)
The `app.py` file uses a hardcoded secret key (`app.secret_key = "dev-secret-key"`). This compromises session security if deployed to production.
**Action:** Load the secret key from an environment variable and fail if not present in production.

## Medium Severity

### 3. Test Configuration Bypass (Reliability)
The integration tests in `tests/expense_tracker/test_routes.py` manually construct a Flask application instance and register the blueprint, bypassing the central `create_app` factory in `app.py`. This risks configuration drift (e.g., missing middleware, error handlers, or config settings present in the main app).
**Action:** Update tests to use the `create_app` factory or a fixture that accurately reflects production configuration.

### 4. Route Integration Mismatch (Correctness)
The tests register the Expense Tracker blueprint at the root (`/`), whereas `app.py` registers it at `/expenses` (`url_prefix="/expenses"`). This means the tests do not verify the routes as they will appear in production.
**Action:** Update integration tests to verify routes at their actual mount point (e.g., `/expenses/`) or ensure the mount point is consistent across environments.

### 5. Debug Mode Enabled (Security)
The `app.py` entry point enables debug mode (`app.run(debug=True)`). While wrapped in `if __name__ == "__main__":`, this configuration can be dangerous if the container executes this file directly in a production-like environment.
**Action:** Use an environment variable to control debug mode or ensure it is disabled by default.

## Low Severity

### 6. Data Persistence Risk (Reliability)
The application uses `InMemoryExpenseRepository`, which stores data in a Python list. All data will be lost upon application restart or deployment.
**Action:** Acknowledge this limitation as technical debt or replacing it with a persistent storage solution (e.g., SQLite file, PostgreSQL) for environments beyond MVP/Testing.

### 7. Missing Logging (Observability)
The `ExpenseService` and routes lack structured logging. Errors are only communicated via `flash` messages to the UI, which may make debugging production issues difficult.
**Action:** Add logging for key events (e.g., expense creation) and errors (e.g., validation failures).
