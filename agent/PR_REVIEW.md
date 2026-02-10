# PR Review Findings

## Critical Severity

### 1. Hardcoded Secret Key (Security)
The `app.py` file sets `app.secret_key = "dev-secret-key"` without loading from environment variables in production. This exposes session signing keys, allowing attackers to forge session cookies and impersonate users.
**Action:** Replace the hardcoded key with `os.environ.get("SECRET_KEY")` and fail if not set in production.

### 2. Unauthenticated Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) and the WebSocket `connect` event are unauthenticated. This allows any network user to read sensitive workflow state or inject false events.
**Action:** Implement authentication checks (e.g., verify a shared secret or token) for both REST endpoints and WebSocket connections.

## High Severity

### 3. Stored XSS Vulnerability (Security)
The `message` field in `MonitorService.update_node` is truncated but not sanitized. Since `monitor.html` renders this field using `innerHTML`, this creates a Stored XSS vulnerability.
**Action:** Sanitize the `message` input in `MonitorService` before storage, or ensure the frontend uses context-aware output encoding.

### 4. Potential File Truncation (Correctness)
The diff for `tests/monitor/test_monitor_routes.py` appears to end abruptly with `data = response.get_jso`. This syntax error will cause test collection failure and break the CI pipeline.
**Action:** Verify the file content is complete and valid before merging.

## Medium Severity

### 5. In-Memory State Consistency (Reliability)
The `MonitorService` relies on in-memory instance variables (`self.nodes`, `self.event_log`). In the production environment using Gunicorn with multiple workers, this state will be inconsistent across requests ("split-brain"), leading to unreliable monitoring data.
**Action:** Move the monitoring state to a shared storage solution (e.g., Redis) or clearly document this limitation and configure Gunicorn to use a single worker.

### 6. Module-Level Global Variables (Maintainability)
`src/sejfa/monitor/monitor_routes.py` uses module-level global variables (`monitor_service`, `socketio`) initialized by `create_monitor_blueprint`. This pattern causes side effects, makes testing brittle, and hinders extensibility.
**Action:** Refactor to use Flask's `current_app.extensions` pattern or a class-based view approach to manage dependencies.

## Low Severity

### 7. Deprecated `datetime.utcnow()` (Maintainability)
`MonitorService._get_timestamp` uses `datetime.utcnow()`, which is deprecated in Python 3.12.
**Action:** Replace with `datetime.now(datetime.timezone.utc)` for future-proof timestamp generation.

### 8. Test Coverage for `max_events` (Test Coverage)
Ensure that `tests/monitor/test_monitor_service.py` includes test cases for `max_events` limit enforcement in `MonitorService.add_event` to prevent unbounded memory growth.
**Action:** Verify or add unit tests for event log rotation.
