# PR Review Findings

## Critical Severity

### 1. Unauthenticated Monitoring Endpoints (Security)
The endpoints `/api/monitor/state` (POST) and `/api/monitor/reset` (POST) in `src/sejfa/monitor/monitor_routes.py` are accessible without authentication. This allows any network-adjacent actor to modify or reset the monitoring state, potentially disrupting operations or injecting false data.
**Action:** Implement authentication checks (e.g., verify a shared secret or token in headers) for all state-mutating endpoints.

## High Severity

### 2. Stored XSS Vulnerability (Security)
The `message` field in `MonitorService.update_node` is truncated but not sanitized. Since `monitor.html` renders this field using `innerHTML` (as per codebase knowledge), this creates a Stored XSS vulnerability.
**Action:** Sanitize the `message` input in `MonitorService` before storage, or ensure the frontend uses context-aware output encoding. Add a test case with a script payload to verify sanitization.

## Medium Severity

### 3. In-Memory State Consistency (Reliability)
The `MonitorService` relies on in-memory instance variables (`self.nodes`, `self.event_log`). In the production environment using Gunicorn with multiple workers, this state will be inconsistent across requests ("split-brain"), leading to unreliable monitoring data.
**Action:** Move the monitoring state to a shared storage solution (e.g., Redis) or clearly document this limitation and configure Gunicorn to use a single worker if acceptable.

### 4. Module-Level Global Variables (Maintainability)
`src/sejfa/monitor/monitor_routes.py` uses module-level global variables (`monitor_service`, `socketio`) initialized by `create_monitor_blueprint`. This pattern causes side effects, makes testing brittle (relying on global state reset), and hinders extensibility.
**Action:** Refactor to use Flask's `current_app.extensions` pattern or a class-based view approach to manage dependencies without global state.

## Low Severity

### 5. Potential File Truncation (Correctness)
The diff for `tests/monitor/test_monitor_routes.py` appears to end abruptly with `data = response.get_jso`. This is likely a syntax error or a truncation issue.
**Action:** Verify the file content is complete and valid before merging.

### 6. Deprecated `datetime.utcnow()` (Maintainability)
`MonitorService._get_timestamp` uses `datetime.utcnow()`, which is deprecated in Python 3.12.
**Action:** Replace with `datetime.now(datetime.timezone.utc)` for future-proof timestamp generation.

### 7. Test Coverage for `max_events` (Test Coverage)
Ensure that `tests/monitor/test_monitor_service.py` includes test cases for `max_events` limit enforcement in `MonitorService.add_event` to prevent unbounded memory growth.
**Action:** Verify or add unit tests for event log rotation.

### 8. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True`. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments.
