# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST /add` endpoint accepts form submissions without a CSRF token, and `Flask-WTF` is neither installed nor configured. This allows attackers to forge requests on behalf of authenticated users.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect` in `app.py`, and add the CSRF token to all forms.

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` uses a predictable token generation mechanism (`hash(username) % 10000`) and relies on hardcoded credentials (`admin`/`admin123`). This allows trivial unauthorized access to administrative functions.
**Action:** Implement secure password hashing (e.g., `bcrypt`) and use cryptographically secure tokens (e.g., `secrets.token_urlsafe`).

## High Severity

### 3. Missing Dependency: flask-socketio (Reliability)
The application imports `flask_socketio` in `app.py`, but this dependency is missing from `requirements.txt`. This will cause the application to fail to start in a fresh environment or CI/CD pipeline.
**Action:** Add `flask-socketio` to `requirements.txt`.

### 4. Insufficient Test Coverage (Reliability)
The test coverage is 78%, falling below the required 80% threshold. Specifically, `src/sejfa/monitor/monitor_routes.py` has only 62% coverage, missing the SocketIO event handlers (`init_socketio_events`) and error handling blocks.
**Action:** Add tests for `init_socketio_events` and error cases in `monitor_routes.py` to reach 80% coverage.

### 5. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. If this code is deployed to production, it compromises session security.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and ensure the application fails to start if it is missing in production.

### 6. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` by default (`socketio.run(app, debug=True, ...)`). This exposes sensitive debugging information and stack traces in the browser if deployed.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

### 7. Unrestricted Monitor API Access (Security)
The `/api/monitor/state` and `/api/monitor/task` endpoints lack authentication, allowing any client to modify the workflow state and inject false events into the dashboard.
**Action:** Implement API key authentication or session-based checks for all state-modifying monitoring endpoints.

## Medium Severity

### 8. Global State in Monitor Routes (Correctness)
`src/sejfa/monitor/monitor_routes.py` relies on global variables (`monitor_service`, `socketio`) in `create_monitor_blueprint`. This prevents multiple application instances (e.g., in tests) and causes race conditions.
**Action:** Refactor `create_monitor_blueprint` to avoid globals, using `current_app.extensions` or a closure to capture dependencies.
