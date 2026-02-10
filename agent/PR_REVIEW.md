# PR Review Findings

## Critical Severity

### 1. Admin Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_` (e.g., `token_fake`), allowing attackers to bypass authentication and access admin endpoints without valid credentials.
**Action:** Implement secure token validation (e.g., store active tokens in a database/memory or use JWT with signature verification).

## High Severity

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin`/`admin123`) in the source code. This is a significant security risk for production deployments.
**Action:** Load credentials from environment variables or a secure vault, and disable the hardcoded fallback in production.

### 3. Incompatible Monitor Client Payload (Correctness)
The `monitor_client.py` sends `action="start"` and `task_id` in `start_task`, but `monitor_routes.py` expects `status` and `start_time` (ignoring `action`). As a result, tasks initiated by the client remain in the "idle" state on the dashboard.
**Action:** Update `monitor_client.py` to send `status="running"` and `start_time` in the payload, or update `monitor_routes.py` to handle the `action` field.

### 4. Thread Safety Issues in MonitorService (Reliability)
The `MonitorService` manages shared state (`nodes`, `event_log`) without any synchronization primitives (e.g., `threading.Lock`). In a multi-threaded Flask environment, this will lead to race conditions and data corruption.
**Action:** Introduce `threading.RLock` to protect access to shared dictionaries and lists in `MonitorService`.

### 5. Missing WebSocket Tests (Test Coverage)
The `monitor` module lacks test coverage. Specifically, `monitor_routes.py` contains significant SocketIO logic that is completely untested (no tests in `tests/monitor/` or `tests/test_app.py`).
**Action:** Add a test suite (e.g., `tests/monitor/test_monitor_socket.py`) using `socketio.test_client(app)` to verify event emission and handling.

## Medium Severity

### 6. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints (e.g., `/api/monitor/state`) are publicly accessible without any authentication. This allows unauthorized users to inject fake events, reset the state, or disrupt monitoring.
**Action:** Implement a simple API key check (e.g., `Authorization: Bearer <KEY>`) or integrate with `AdminAuthService`.

### 7. Test Isolation Leak in stop-hook tests (Test Quality)
The `tests/agent/test_stop_hook.py` fixture `stop_hook` modifies `sys.modules["monitor_client"]` globally but fails to restore it after the test. This can cause subsequent tests that rely on the real `monitor_client` to fail or behave unpredictably.
**Action:** Use `mock.patch.dict(sys.modules, ...)` or manually restore `sys.modules` in a `yield` fixture teardown.

## Low Severity

### 8. Global State in Monitor Routes (Maintainability)
The `src/sejfa/monitor/monitor_routes.py` module relies on global variables `monitor_service` and `socketio`, which are injected via `create_monitor_blueprint`. This pattern makes the module difficult to test and reuse, and prone to initialization order issues.
**Action:** Refactor to use Flask's `current_app` extensions or dependency injection via closure/class-based views.
