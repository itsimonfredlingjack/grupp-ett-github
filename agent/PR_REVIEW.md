# PR Review Findings

## High Severity

### 1. Unprotected Monitor Endpoints (Security)
The endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are publicly accessible without authentication. This allows any network user to inject false events or reset the monitoring state, potentially disrupting operations.
**Action:** Implement authentication (e.g., API key or shared secret) for all monitor endpoints.

### 2. Split-Brain State in Monitor Service (Reliability)
The `MonitorService` uses in-memory dictionaries (`self.nodes`, `self.event_log`) to store state. Since the deployment uses `gunicorn` with multiple workers (as noted in memory), each worker will maintain its own separate state. This leads to a "split-brain" scenario where updates sent to one worker are not reflected in the state retrieved by clients connected to another worker via WebSockets.
**Action:** Use a shared state store like Redis or a database to ensure consistency across all workers, or configure gunicorn to use a single worker for the monitor service if scalability is not a concern.

## Medium Severity

### 3. Error Handling Masks BadRequest (Correctness)
The `update_state` and other routes in `src/sejfa/monitor/monitor_routes.py` wrap `request.get_json()` in a broad `try...except Exception` block. If `get_json()` fails (e.g., malformed JSON), it raises `werkzeug.exceptions.BadRequest` (400), which is caught and returned as a 500 Internal Server Error. This misleadingly suggests a server failure instead of a client error.
**Action:** Use `request.get_json(silent=True)` and check for `None`, or catch `werkzeug.exceptions.BadRequest` explicitly and return a 400 status code.

### 4. Missing WebSocket Test Coverage (Test Coverage)
The new test file `tests/monitor/test_monitor_routes.py` mocks `SocketIO` but does not verify that WebSocket events are actually emitted. The `init_socketio_events` function is called, but interactions with `socketio.emit` are not asserted. This leaves the core real-time functionality untested.
**Action:** Update the tests to use `socketio_client` or mock `socketio.emit` to verify that state updates are correctly broadcast to connected clients.

## Low Severity

### 5. Deprecated `datetime.utcnow()` Usage (Maintainability)
Both `src/sejfa/monitor/monitor_routes.py` and `src/sejfa/monitor/monitor_service.py` use `datetime.utcnow()`, which is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.
