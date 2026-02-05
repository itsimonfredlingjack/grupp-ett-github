# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks CSRF protection on form submissions (e.g., Expense Form), allowing attackers to forge requests.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include CSRF tokens in all forms.

### 2. Weak Admin Authentication (Security)
`AdminAuthService` uses predictable token generation and hardcoded credentials (`admin`/`admin123`).
**Action:** Implement secure password hashing (e.g., `bcrypt`) and cryptographically secure tokens.

### 3. Missing Authentication on Monitor Endpoints (Security)
The `/api/monitor/*` endpoints are publicly accessible, allowing unprivileged users to modify the monitoring state.
**Action:** Implement authentication (e.g., Admin Token check) for all state-modifying monitor endpoints.

## High Severity

### 4. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`.
**Action:** Load `SECRET_KEY` from environment variables and fail if missing in production.

### 5. Debug Mode Enabled (Security)
The application runs with `debug=True` and `allow_unsafe_werkzeug=True` in `app.py`.
**Action:** Configure debug mode via environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

### 6. Global State in Monitor Blueprint (Reliability)
`monitor_routes.py` relies on module-level `global` variables (`monitor_service`, `socketio`), compromising thread safety and testability.
**Action:** Refactor `create_monitor_blueprint` to avoid globals, using `current_app` or closure-based dependency injection.

## Medium Severity

### 7. Unsafe Float Conversion (Correctness)
The `Expense` model uses `float` for monetary values, causing potential precision errors and accepting `NaN`/`Infinity`.
**Action:** Use `decimal.Decimal` for all monetary fields and conversions.

### 8. Untested SocketIO Events (Reliability)
The tests in `tests/monitor/test_monitor_routes.py` do not verify SocketIO event handlers (`connect`, `request_state`), leaving `init_socketio_events` untested.
**Action:** Add tests using `socketio_client` to verify WebSocket event emission and handling.
