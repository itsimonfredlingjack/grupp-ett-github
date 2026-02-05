# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST` endpoints (e.g., `/add`, `/admin/login`) accept form submissions without a CSRF token. This allows attackers to forge requests on behalf of authenticated users.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect` in `app.py`, and add the CSRF token to all forms.

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` uses a predictable token generation mechanism (`hash(username) % 10000`) and relies on hardcoded credentials (`admin`/`admin123`). This allows trivial unauthorized access to administrative functions.
**Action:** Implement secure password hashing (e.g., `bcrypt`) and use cryptographically secure tokens (e.g., `secrets.token_urlsafe`).

## High Severity

### 3. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. If this code is deployed to production, it compromises session security.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and ensure the application fails to start if it is missing in production.

### 4. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` by default (`socketio.run(app, debug=True, ...)`). This exposes sensitive debugging information and stack traces in the browser if deployed.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

### 5. Missing Dependencies (Reliability)
The application imports `flask_socketio` in `app.py`, but it is not listed in `requirements.txt`. This causes the application to fail to start in a fresh environment.
**Action:** Add `flask-socketio` (and `Flask-WTF`) to `requirements.txt`.

### 6. Insufficient Test Coverage (Reliability)
Test coverage is likely below 80% due to the new monitoring components (`src/sejfa/monitor/`) which lack unit tests entirely (`tests/monitor/` does not exist).
**Action:** Add unit and integration tests for `MonitorService` and `monitor_routes` to meet the coverage threshold.

## Medium Severity

### 7. Unsafe Float for Currency (Correctness)
The `Expense` model uses `float` for the `amount` field. Floating-point arithmetic can introduce precision errors unsuitable for financial calculations.
**Action:** Use `decimal.Decimal` for currency values to ensure precision.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas requirements often mandate `sqlite:///:memory:` for in-memory persistence simulation.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify requirements.
