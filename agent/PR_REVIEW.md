# PR Review Findings

## Critical Severity

### 1. Hardcoded Secret Key in Application Factory (Security)
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 2. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 3. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` dashboard renders `event.message` using `innerHTML` without sanitization. An attacker can inject malicious scripts via the unauthenticated `/api/monitor/state` endpoint, leading to Stored Cross-Site Scripting (XSS).
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify before rendering.

## High Severity

### 4. Unauthenticated Monitor Endpoints (Security)
The `/api/monitor/state` and `/api/monitor/task` endpoints in `src/sejfa/monitor/monitor_routes.py` allow unauthenticated users to modify the monitoring state. This allows injection of false data or disruption of the dashboard.
**Action:** Implement authentication (e.g., verify the Admin Session Token or a dedicated API key) for these endpoints.

## Medium Severity

### 5. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. Using SQLite ensures the application is ready for SQL-based persistence.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database.

## Low Severity

### 6. Global State in Monitor Blueprint (Quality)
The `src/sejfa/monitor/monitor_routes.py` module relies on global variables (`monitor_service`, `socketio`) for dependency injection. This makes testing difficult and violates thread-safety best practices.
**Action:** Use Flask's `current_app` extensions or closure-based view functions to pass dependencies.

### 7. Inconsistent Route Registration in Tests (Quality)
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at `/`, while `app.py` registers it at `/expenses`. This discrepancy creates a mismatch between test and production environments.
**Action:** Update the test fixture to register the blueprint at `/expenses` or use the `create_app` factory in tests.
