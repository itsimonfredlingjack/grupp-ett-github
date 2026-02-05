# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST` endpoints (e.g., `/add`, `/admin/login`) accept form submissions without a CSRF token. This allows attackers to forge requests on behalf of authenticated users.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect` in `app.py`, and add the CSRF token to all forms.

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` uses a predictable token generation mechanism (`hash(username) % 10000`) and relies on hardcoded credentials (`admin`/`admin123`). Additionally, `validate_session_token` allows any token starting with `token_` to bypass authentication.
**Action:** Implement secure password hashing (e.g., `bcrypt`), use cryptographically secure tokens (e.g., `secrets.token_urlsafe`), and fix the validation logic.

### 3. Missing Authentication on Monitor Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/api/monitor/reset`, `/api/monitor/task`) are unprotected, allowing unauthenticated users to manipulate the agent workflow state and inject fake events.
**Action:** Apply the `@require_admin_token` decorator to all state-changing endpoints in `src/sejfa/monitor/monitor_routes.py`.

## High Severity

### 4. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. If this code is deployed to production, it compromises session security.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and ensure the application fails to start if it is missing in production.

### 5. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` by default (`socketio.run(app, debug=True, ...)`). This exposes sensitive debugging information and stack traces in the browser if deployed.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

## Medium Severity

### 6. Missing CI Script (Reliability)
The script `scripts/preflight.sh` is required by the `jules_health_check.yml` workflow but is missing from the repository. This will cause the health check workflow to fail consistently.
**Action:** Restore or create `scripts/preflight.sh` to ensure CI pipeline integrity.

### 7. Missing Dependencies (Reliability)
The application imports `flask_socketio` in `app.py` and requires `Flask-WTF` for CSRF protection, but neither is listed in `requirements.txt`. This causes the application to fail to start in a fresh environment.
**Action:** Add `flask-socketio` and `Flask-WTF` to `requirements.txt`.

### 8. Insufficient Test Coverage (Reliability)
Test coverage is likely below 80% due to the new monitoring components (`src/sejfa/monitor/`) which lack unit tests entirely (`tests/monitor/` does not exist).
**Action:** Add unit and integration tests for `MonitorService` and `monitor_routes` to meet the coverage threshold.
