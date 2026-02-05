# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST /add` endpoint accepts form submissions without a CSRF token, and `Flask-WTF` is neither installed nor configured. This allows attackers to forge requests on behalf of authenticated users.
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
Test coverage is 74%, falling below the required 80%. The new monitoring components (`src/sejfa/monitor/`) have significantly low coverage (`monitor_routes.py`: 28%, `monitor_service.py`: 36%).
**Action:** Add unit and integration tests for `MonitorService` and `monitor_routes` to meet the coverage threshold.

## Medium Severity

### 7. Unsafe Float Conversion (Correctness)
The `Expense` model and routes use `float` for monetary values. This leads to precision errors and allows `Infinity` and `NaN` values, which are inappropriate for currency.
**Action:** Use `decimal.Decimal` for monetary values and validate input to reject non-numeric or special values.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. This discrepancy reduces the validity of tests regarding database constraints.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database to match production-like behavior.
