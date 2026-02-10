# PR Review Findings

## High Severity

### 1. Authentication Bypass (Security)
Monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`, `/reset`) are unprotected. Anyone with network access can manipulate the monitoring state or reset it.
**Action:** Implement authentication (e.g., `@login_required` or API key validation) for all sensitive monitoring endpoints.

## Medium Severity

### 2. Global State Dependency (Reliability)
The `src/sejfa/monitor/monitor_routes.py` module relies on module-level global variables (`monitor_service`, `socketio`) which are injected via `create_monitor_blueprint`. This pattern makes testing difficult and can cause race conditions in a multi-worker environment (e.g., gunicorn).
**Action:** Refactor to use a proper dependency injection pattern or Flask's `current_app` context to store service instances.
