# PR Review Findings

## Critical Severity

### 1. Thread Safety Violation (Correctness)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` uses unprotected shared state (`nodes`, `event_log`) without any locking mechanism (`threading.RLock`). Since `MonitorService` is instantiated as a singleton and used across concurrent requests (e.g., via Flask/Gunicorn threads), race conditions can corrupt the event log or node states.
**Action:** Add `threading.RLock` to `MonitorService` and protect all state mutations (`update_node`, `reset`, `add_event`).

## High Severity

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/api/monitor/reset`) in `src/sejfa/monitor/monitor_routes.py` are publicly accessible without authentication. Tests like `test_update_state` confirm that no authorization headers are required. This allows unauthenticated users to inject false events or reset the monitoring system.
**Action:** Implement authentication (e.g., API key or token validation) for all state-modifying endpoints.

## Medium Severity

### 3. Global State Leak in Test Fixture (Reliability)
The `stop_hook` fixture in `tests/agent/test_stop_hook.py` modifies `sys.modules['monitor_client']` globally but fails to restore the original state after the test. This pollutes the global namespace for subsequent tests, potentially masking import errors or causing flaky tests.
**Action:** Use `unittest.mock.patch.dict(sys.modules, ...)` or a `try...finally` block to restore `sys.modules`.

### 4. Mutable Global State in Blueprints (Reliability)
`src/sejfa/monitor/monitor_routes.py` uses module-level global variables (`monitor_service`, `socketio`) that are overwritten by `create_monitor_blueprint`. This prevents running multiple app instances or parallel tests involving this blueprint.
**Action:** Store dependencies in `current_app.extensions` or `current_app.config` instead of module globals.

### 5. Missing WebSocket Coverage (Test Coverage)
The `tests/monitor/test_monitor_routes.py` suite only covers HTTP endpoints. The WebSocket event handlers (`connect`, `request_state`) in `init_socketio_events` are entirely untested, leaving critical real-time functionality unverified.
**Action:** Add tests using `socketio.test_client(app)` to verify WebSocket connectivity and event handling.

## Low Severity

### 6. Missing Mock Assertions (Test Coverage)
In `test_monitor_routes.py`, `socketio` is mocked, but the tests do not assert that `emit` is called when state changes. This means the tests would pass even if the broadcasting logic was removed.
**Action:** Add assertions like `socketio.emit.assert_called_with(...)` to verify that state updates are correctly broadcast to clients.
