# PR Review Findings

## Critical Severity

### 1. Missing Authentication on Monitor Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/api/monitor/reset`, `/api/monitor/task`) in `src/sejfa/monitor/monitor_routes.py` are unprotected. This allows unauthenticated users to manipulate the agent workflow state and inject fake events.
**Action:** Apply the `@require_admin_token` decorator (or similar auth check) to all state-changing endpoints.

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` uses a predictable token generation mechanism (`hash(username) % 10000`) and relies on hardcoded credentials (`admin`/`admin123`). Additionally, `validate_session_token` allows any token starting with `token_` to bypass authentication.
**Action:** Implement secure password hashing (e.g., `bcrypt`), use cryptographically secure tokens (e.g., `secrets.token_urlsafe`), and fix the validation logic.

## High Severity

### 3. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST` endpoints (e.g., `/expenses/add`, `/admin/login`) accept form submissions without a CSRF token. This allows attackers to forge requests on behalf of authenticated users.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect` in `app.py`, and add the CSRF token to all forms.

### 4. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. If this code is deployed to production, it compromises session security.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and ensure the application fails to start if it is missing in production.

### 5. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` by default (`socketio.run(app, debug=True, ...)`). This exposes sensitive debugging information and stack traces in the browser if deployed.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

## Medium Severity

### 6. Missing CI Script (Reliability)
The script `scripts/preflight.sh` is required by the `jules_health_check.yml` workflow but is missing from the repository. This causes CI failures.
**Action:** Create `scripts/preflight.sh` with the necessary health checks.

### 7. Inappropriate Data Type for Currency (Correctness)
The `Expense` model uses `float` for the `amount` field. Floating-point arithmetic can lead to precision errors in financial calculations.
**Action:** Use `decimal.Decimal` for currency values in the `Expense` model and related database columns.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. Using SQLite ensures readiness for SQL-based persistence.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database.
