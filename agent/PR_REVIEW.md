# PR Review Findings

## Critical Severity

### 1. Regression in ci_branch.yml (CI Breakage)
The PR removes `pip install -r requirements.txt` from `.github/workflows/ci_branch.yml`. This will cause CI failures as dependencies like `flask-socketio` (required by the tests) will not be installed.
**Action:** Revert the changes to `.github/workflows/ci_branch.yml` or restore the `pip install -r requirements.txt` command.

### 2. Regression in self_healing.yml (Infinite Loop Risk)
The PR removes the `[skip-jules-review]` marker from the auto-fix commit message in `.github/workflows/self_healing.yml`. This prevents the review workflow from skipping these automated commits, potentially triggering a loop.
**Action:** Restore the `[skip-jules-review]` marker in the commit message.

## High Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 4. Thread Safety in MonitorService (Reliability)
`MonitorService` in `src/sejfa/monitor/monitor_service.py` modifies shared state (`self.nodes`, `self.event_log`) without locking. This is not thread-safe and may cause race conditions in a multi-threaded environment.
**Action:** Add `threading.Lock` to protect shared state modifications.

### 5. Untested Socket Event Handlers (Test Coverage)
`tests/monitor/test_monitor_routes.py` registers socket handlers via `init_socketio_events` but never executes the logic inside them (`handle_connect`, `handle_request_state`). This leaves the WebSocket communication logic effectively untested.
**Action:** Update the test to manually invoke the registered handlers or mock the client connection to trigger them.

## Medium Severity

### 6. Test Isolation Leak in stop_hook Fixture (Reliability)
The `stop_hook` fixture in `tests/agent/test_stop_hook.py` modifies `sys.modules["monitor_client"]` but fails to restore it after the test. This side effect can break other tests that rely on the real `monitor_client` or its absence.
**Action:** Use `mock.patch.dict(sys.modules, ...)` or manually restore `sys.modules` in a `yield` fixture pattern.

## Low Severity

### 7. Global State Usage in Blueprint Factory (Reliability)
`src/sejfa/monitor/monitor_routes.py` relies on module-level global variables (`monitor_service`, `socketio`) initialized in `create_monitor_blueprint`. This prevents support for multiple application instances and causes state leakage between tests.
**Action:** Refactor `create_monitor_blueprint` to close over dependencies or use `current_app.extensions` instead of globals.

### 8. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).
