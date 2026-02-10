# PR Review Findings

## High Severity

### 1. Incompatible Monitor Client Payload (Correctness)
The `monitor_client.py` sends `action="start"` and `task_id` in `start_task`, but `monitor_routes.py` expects `status` and `start_time` (ignoring `action`). As a result, tasks initiated by the client remain in the "idle" state on the dashboard.
**Action:** Update `monitor_client.py` to send `status="running"` and `start_time` in the payload, or update `monitor_routes.py` to handle the `action` field.

### 2. Thread Safety Issues in MonitorService (Reliability)
The `MonitorService` manages shared state (`nodes`, `event_log`) without any synchronization primitives (e.g., `threading.Lock`). In a multi-threaded Flask environment, this will lead to race conditions and data corruption.
**Action:** Introduce `threading.RLock` to protect access to shared dictionaries and lists in `MonitorService`.

## Medium Severity

### 3. Test Isolation Leak in stop-hook tests (Test Quality)
The `tests/agent/test_stop_hook.py` fixture `stop_hook` modifies `sys.modules["monitor_client"]` globally but fails to restore it after the test. This can cause subsequent tests that rely on the real `monitor_client` to fail or behave unpredictably.
**Action:** Use `mock.patch.dict(sys.modules, ...)` or manually restore `sys.modules` in a `yield` fixture teardown.

### 4. Missing WebSocket Tests (Test Coverage)
The new test suite `tests/monitor/test_monitor_routes.py` covers REST endpoints but completely lacks coverage for WebSocket events (`connect`, `disconnect`, `state_update`). The `monitor_routes.py` module contains significant SocketIO logic that is currently untested.
**Action:** Add a test file (e.g., `tests/monitor/test_monitor_socket.py`) using `socketio.test_client(app)` to verify event emission and handling.

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints (e.g., `/api/monitor/state`) are publicly accessible without any authentication. This allows unauthorized users to inject fake events, reset the state, or disrupt monitoring.
**Action:** Implement a simple API key check (e.g., `Authorization: Bearer <KEY>`) or integrate with `AdminAuthService`.

## Low Severity

### 6. Global State in Monitor Routes (Maintainability)
The `src/sejfa/monitor/monitor_routes.py` module relies on global variables `monitor_service` and `socketio`, which are injected via `create_monitor_blueprint`. This pattern makes the module difficult to test and reuse, and prone to initialization order issues.
**Action:** Refactor to use `current_app` extensions or a proper dependency injection pattern.

### 7. Deprecated datetime.utcnow() Usage (Reliability)
The code uses `datetime.utcnow()`, which is deprecated in Python 3.12. It returns a naive datetime object that can cause timezone confusion.
**Action:** Replace with `datetime.now(datetime.timezone.utc)`.
