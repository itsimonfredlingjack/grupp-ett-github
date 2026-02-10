# PR Review Findings

## Critical Severity

### 1. In-Memory State in Multi-Worker Environment (Reliability)
The `MonitorService` relies on in-memory dictionaries (`self.nodes`, `self.event_log`) to track state. In a production environment running with `gunicorn` and multiple workers, this state will be fragmented across processes, leading to inconsistent monitoring data (split-brain).
**Action:** Use a shared data store (e.g., Redis or a database) for `MonitorService` state, or configure `gunicorn` to use a single worker with threads (though thread safety must still be addressed).

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are completely unauthenticated. This allows any network user to inject false events, reset the dashboard, or disrupt the monitoring service.
**Action:** Implement authentication for these endpoints, such as requiring an API key or a shared secret header, and validate it in a `before_request` handler or decorator.

## Medium Severity

### 3. API Schema Mismatch (Correctness)
There is a schema mismatch between the client and server implementations for task updates:
- `monitor_client.py` sends `action` ("start", "complete") and `task_id`.
- `monitor_routes.py` expects `status` ("idle", "running", "completed") and ignores `action` and `task_id`.
This prevents the dashboard from correctly tracking task start/completion events.
**Action:** Update `monitor_routes.py` to handle the `action` field and map "start"/"complete" to appropriate status updates, or update `monitor_client.py` to send the expected `status` field.

### 4. Incomplete Test Coverage (Testing)
The new test `test_update_state_success` in `tests/monitor/test_monitor_routes.py` appears to lack assertions, making it a "happy path" check that doesn't verify the actual outcome (status code or response body).
**Action:** Add assertions to verify `response.status_code == 200` and that the returned JSON contains the expected state.

## Low Severity

### 5. Use of Global Variables (Maintainability)
The `monitor_routes.py` module relies on module-level global variables (`monitor_service`, `socketio`) which are populated via `create_monitor_blueprint`. This makes testing difficult (requiring global state management) and is not thread-safe if the module is reloaded.
**Action:** Register these services on `current_app` or use the `g` object to ensure proper application context and thread safety.

### 6. Hardcoded Node Configuration (Maintainability)
The list of valid nodes (`jira`, `claude`, `github`, `jules`, `actions`) is hardcoded in `MonitorService.VALID_NODES`. Adding a new agent or tool requires code changes to the service.
**Action:** Move the valid node list to a configuration file or allow dynamic registration of nodes.

### 7. Unsafe Development Configuration (Security)
The `app.py` entry point enables `debug=True` and `allow_unsafe_werkzeug=True` in the `__main__` block. While this only affects direct execution, it poses a risk if the application is started this way in a production-like environment.
**Action:** Ensure these settings are disabled in production, preferably by using environment variables (e.g., `FLASK_DEBUG`) to control debug mode.
