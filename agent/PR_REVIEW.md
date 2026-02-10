# PR Review Findings

## Critical Severity

### 1. Regression in Workflow Trigger (Correctness)
The PR re-introduces `synchronize` and `reopened` triggers to `.github/workflows/jules_review.yml`, which were intentionally removed to prevent feedback loops. This regression causes the workflow to run on every push, potentially creating infinite loops with automated commits.
**Action:** Remove `synchronize` and `reopened` from the `on: pull_request: types` list.

### 2. Thread Safety Violation (Correctness)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` uses unprotected shared state (`nodes`, `event_log`) without any locking mechanism. Since `MonitorService` is instantiated as a singleton and accessed concurrently (e.g., via Flask threads), race conditions can corrupt internal state.
**Action:** Add `threading.RLock` to `MonitorService` and protect all state mutations (`update_node`, `reset`, `add_event`).

## High Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/api/monitor/reset`, `/api/monitor/task`) in `src/sejfa/monitor/monitor_routes.py` are publicly accessible without authentication. This allows unauthenticated users to inject false events, reset the monitoring system, or modify task state.
**Action:** Implement authentication (e.g., API key or token validation) for all state-modifying endpoints.

### 4. Protocol Mismatch (Correctness)
The `monitor_client.py` hook sends `action="start"` and `task_id` when starting a task, but `monitor_routes.py`'s `/task` endpoint ignores these fields and expects `status`. As a result, task updates from the hook fail to transition the task status correctly.
**Action:** Update `monitor_routes.py` to handle `action` and `task_id` fields, or update `monitor_client.py` to send `status`.

## Medium Severity

### 5. Global State Leak in Test Fixture (Reliability)
The `stop_hook` fixture in `tests/agent/test_stop_hook.py` modifies `sys.modules['monitor_client']` globally but fails to restore the original state after the test. This pollutes the global namespace for subsequent tests.
**Action:** Use `unittest.mock.patch.dict(sys.modules, ...)` or a `try...finally` block to restore `sys.modules`.

### 6. Mutable Global State in Blueprints (Reliability)
`src/sejfa/monitor/monitor_routes.py` uses module-level global variables (`monitor_service`, `socketio`) that are overwritten by `create_monitor_blueprint`. This prevents running multiple app instances or parallel tests involving this blueprint.
**Action:** Store dependencies in `current_app.extensions` or `current_app.config` instead of module globals.

### 7. Missing Monitor Tests (Test Coverage)
The file `tests/monitor/test_monitor_routes.py` (referenced in previous findings) does not exist. Consequently, the monitoring endpoints (especially WebSocket events like `connect` and `request_state`) are completely untested.
**Action:** Create `tests/monitor/test_monitor_routes.py` and add tests for HTTP endpoints and WebSocket events.
