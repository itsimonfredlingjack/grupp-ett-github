# PR Review Findings

## High Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 2. Thread Safety in MonitorService (Reliability)
`MonitorService` in `src/sejfa/monitor/monitor_service.py` modifies shared state (`self.nodes`, `self.event_log`) without locking. This is not thread-safe and may cause race conditions in a multi-threaded environment.
**Action:** Add `threading.Lock` to protect shared state modifications.

### 3. Untested Socket Event Handlers (Test Coverage)
`tests/monitor/test_monitor_routes.py` registers socket handlers via `init_socketio_events` but never executes the logic inside them (`handle_connect`, `handle_request_state`). This leaves the WebSocket communication logic effectively untested.
**Action:** Update the test to manually invoke the registered handlers or mock the client connection to trigger them.

## Medium Severity

### 4. Test Isolation Leak in stop_hook Fixture (Reliability)
The `stop_hook` fixture in `tests/agent/test_stop_hook.py` modifies `sys.modules["monitor_client"]` but fails to restore it after the test. This side effect can break other tests that rely on the real `monitor_client` or its absence.
**Action:** Use `mock.patch.dict(sys.modules, ...)` or manually restore `sys.modules` in a `yield` fixture pattern.

## Low Severity

### 5. Global State Usage in Blueprint Factory (Reliability)
`src/sejfa/monitor/monitor_routes.py` relies on module-level global variables (`monitor_service`, `socketio`) initialized in `create_monitor_blueprint`. This prevents support for multiple application instances and causes state leakage between tests.
**Action:** Refactor `create_monitor_blueprint` to close over dependencies or use `current_app.extensions` instead of globals.

### 6. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).
