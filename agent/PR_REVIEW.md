# PR Review Findings

## Critical Severity

### 1. Thread Safety Issues in MonitorService (Correctness)
The `MonitorService` relies on unprotected in-memory dictionaries (`self.nodes`, `_subscribers`), causing thread-safety issues. When deployed with multiple workers (e.g., using gunicorn), this leads to a "split-brain" state where each worker maintains its own state, resulting in inconsistent monitoring data.
**Action:** Use an external store (e.g., Redis) or a database for state management to ensure consistency across workers.

## High Severity

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`) are unauthenticated. This allows unauthorized users to manipulate the monitoring state or reset the dashboard.
**Action:** Implement authentication for these endpoints, possibly reusing `AdminAuthService` or introducing an API key mechanism.

### 3. Unsafe Application Configuration (Security)
The application is configured to run with `debug=True` and `allow_unsafe_werkzeug=True` in `app.py`. This exposes the Werkzeug debugger and allows arbitrary code execution if exposed to the internet.
**Action:** Ensure these settings are disabled in production, or controlled via environment variables (e.g., `FLASK_DEBUG`).

## Medium Severity

### 4. Global State in Monitor Routes (Reliability)
The `src/sejfa/monitor/monitor_routes.py` module uses module-level global variables (`monitor_service`, `socketio`). This makes the code harder to test and maintain, and can lead to state leakage between tests.
**Action:** Refactor to use Flask's `current_app` context or dependency injection patterns supported by Flask-Injector.

## Low Severity

### 5. Dead Code in `stop-hook.py` (Maintainability)
The `stop-hook.py` script contains a try-except block importing from `monitor_client`, which is mocked in tests. While the client exists, the import logic in the hook is fragile and seemingly unused if the hook is running in a different environment.
**Action:** Verify if `monitor_client` is intended to be used by the hook and ensure it is importable, or remove the import if unnecessary.

### 6. Hardcoded Secrets (Security)
The `app.py` uses a hardcoded `secret_key` ("dev-secret-key") if not provided by environment.
**Action:** Enforce loading from environment variables and fail if not present in production.
