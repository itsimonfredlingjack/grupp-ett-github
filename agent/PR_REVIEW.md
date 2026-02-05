# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. `Flask-WTF` is missing from `requirements.txt` and `CSRFProtect` is not initialized in `app.py`.
**Action:** Install `Flask-WTF` and initialize `CSRFProtect` in `app.py`.

## High Severity

### 2. Thread Safety in MonitorService (Reliability)
The `MonitorService.update_node` method modifies shared state (`self.nodes`) without locking, causing race conditions in threaded environments.
**Action:** Implement `threading.Lock` around state modifications.

### 3. Missing Automated Tests for Monitoring (Test Coverage)
The `tests/monitor/` directory is missing, leaving the monitoring feature (`src/sejfa/monitor/`) without automated test coverage.
**Action:** Add unit and integration tests for `MonitorService` and `monitor_routes`.

### 4. Weak Admin Authentication (Security)
`AdminAuthService` relies on predictable tokens and hardcoded credentials.
**Action:** Use secure token generation and password hashing.

### 5. Hardcoded Secret Key (Security)
`app.secret_key` is hardcoded to "dev-secret-key" in `app.py`.
**Action:** Load `SECRET_KEY` from environment variables.

### 6. Debug Mode Enabled (Security)
`socketio.run(app, debug=True)` is enabled by default in the entry point.
**Action:** Disable debug mode or use an environment variable.

## Medium Severity

### 7. Missing Flask-WTF Dependency (Dependencies)
`Flask-WTF` is required for CSRF protection but is missing from `requirements.txt`.
**Action:** Add `Flask-WTF` to `requirements.txt`.

### 8. Deprecated datetime.utcnow (Reliability)
`MonitorService` uses `datetime.utcnow()`, which is deprecated.
**Action:** Use `datetime.now(timezone.utc)`.
