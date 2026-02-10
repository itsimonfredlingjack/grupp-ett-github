# PR Review Findings

## Critical Severity

### 1. In-Memory State in Multi-Worker Environment (Reliability)
The `MonitorService` relies on in-memory dictionaries (`self.nodes`, `self.event_log`) to track state. In a production environment running with `gunicorn` and multiple workers, this state will be fragmented across processes, leading to inconsistent monitoring data (split-brain).
**Action:** Use a shared data store (e.g., Redis or a database) for `MonitorService` state, or configure `gunicorn` to use a single worker with threads (though thread safety must still be addressed).

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are completely unauthenticated. This allows any network user to inject false events, reset the dashboard, or disrupt the monitoring service.
**Action:** Implement authentication for these endpoints, such as requiring an API key or a shared secret header, and validate it in a `before_request` handler or decorator.

## High Severity

### 3. Mutable State Leak in get_state (Reliability)
`MonitorService.get_state()` returns the internal `self.event_log` list and `self.task_info` dictionary directly. Modifying the returned structures (e.g., in a test or consumer) affects the service's internal state, violating encapsulation and snapshot semantics.
**Action:** Return deep copies of these structures (e.g., `list(self.event_log)` or `copy.deepcopy()`) to ensure the returned state is a true snapshot.

## Medium Severity

### 4. API Schema Mismatch (Correctness)
There is a schema mismatch between the client and server implementations for task updates:
- `monitor_client.py` sends `action` ("start", "complete") and `task_id`.
- `monitor_routes.py` expects `status` ("idle", "running", "completed") and ignores `action` and `task_id`.
This prevents the dashboard from correctly tracking task start/completion events.
**Action:** Update `monitor_routes.py` to handle the `action` field and map "start"/"complete" to appropriate status updates, or update `monitor_client.py` to send the expected `status` field.

### 5. Use of Global Variables (Maintainability)
The `monitor_routes.py` module relies on module-level global variables (`monitor_service`, `socketio`) which are populated via `create_monitor_blueprint`. This makes testing difficult (requiring global state management) and is not thread-safe if the module is reloaded.
**Action:** Register these services on `current_app` or use the `g` object to ensure proper application context and thread safety.

## Low Severity

### 6. Deprecated datetime.utcnow() (Reliability)
The codebase uses `datetime.utcnow()` in multiple places (e.g., `monitor_service.py`, `monitor_routes.py`). This method is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace with `datetime.now(timezone.utc)` to ensure future compatibility.

### 7. Stop-Hook Triggered by Code Blocks (Security)
As noted in `tests/agent/test_stop_hook.py`, the `stop-hook.py` script will trigger a stop if the completion promise (`<promise>DONE</promise>`) appears inside a code block in the transcript. This could lead to premature termination if the agent is merely quoting the promise.
**Action:** Improve the regex or parsing logic to ignore code blocks when scanning for the completion promise.

### 8. Unsafe Development Configuration (Security)
The `app.py` entry point enables `debug=True` and `allow_unsafe_werkzeug=True` in the `__main__` block. While this only affects direct execution, it poses a risk if the application is started this way in a production-like environment.
**Action:** Ensure these settings are disabled in production, preferably by using environment variables (e.g., `FLASK_DEBUG`) to control debug mode.
