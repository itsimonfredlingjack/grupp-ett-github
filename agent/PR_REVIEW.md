# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`admin`, `admin123`). This allows unauthorized access if deployed.
**Action:** Move credentials to environment variables or a secure database.

## High Severity

### 2. Insecure Session Token Validation (Security)
`AdminAuthService.validate_session_token` accepts any token starting with `token_`, allowing authentication bypass.
**Action:** Implement proper token validation (e.g., JWT verification or secure session lookup).

### 3. Unprotected Monitoring Endpoints (Security)
Monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) lack authentication.
**Action:** Secure endpoints with `@login_required` or API key validation.

## Medium Severity

### 4. Monitor Client Incompatibility (Reliability)
The `monitor_client.py` script sends `action` and `task_id` fields for task updates, but the server endpoint `POST /api/monitor/task` in `monitor_routes.py` expects `status` and ignores `action`. This prevents task status updates from being reflected on the dashboard.
**Action:** Update `monitor_routes.py` to handle `action` fields or update `monitor_client.py` to send `status`.

### 5. In-Memory State Synchronization Issue (Reliability)
`MonitorService` stores state in-memory, leading to inconsistent data across multiple Gunicorn workers ("split-brain").
**Action:** Use an external store (e.g., Redis) or database for shared state.

### 6. Race Conditions in MonitorService (Reliability)
`MonitorService` updates shared state (`self.nodes`, `self.event_log`) without locking, risking data corruption.
**Action:** Add thread synchronization (e.g., `threading.Lock`) for state updates.

## Low Severity

### 7. Unsafe Application Configuration (Security)
`app.py` enables `debug=True` and `allow_unsafe_werkzeug=True` in the `__main__` block.
**Action:** Ensure these settings are disabled in production environments.
