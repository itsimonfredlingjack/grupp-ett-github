# Automated PR Review Findings

## High Severity

### 1. Unauthenticated Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (`/state`, `/reset`, `/task`) are publicly accessible without authentication. This allows unauthorized users to manipulate the monitoring state.
**Action:** Implement authentication (e.g., `@login_required` or token check).

### 2. In-Memory State & Split-Brain (Reliability)
`MonitorService` relies on in-memory dictionaries (`self.nodes`, `self.event_log`). In a production environment with multiple Gunicorn workers (as indicated by `CURRENT_TASK.md`), each worker will maintain isolated state, causing inconsistent data ("split-brain").
**Action:** Use an external state store (e.g., Redis) or ensure sticky sessions if using single-process deployment.

### 3. Lack of Thread Safety (Reliability)
`MonitorService` modifies shared state without locks (`threading.RLock`). Concurrent requests can race and corrupt data, leading to unpredictable behavior.
**Action:** Add thread safety mechanisms (locks) around state modifications.

### 4. Broken CI Configuration (Reliability)
The `.github/workflows/ci_branch.yml` workflow installs dependencies manually (`pip install pytest ... flask`) and omits `flask-socketio`. The new tests in `tests/monitor/test_monitor_routes.py` depend on `flask-socketio`, so CI will fail with `ImportError`.
**Action:** Update the workflow to `pip install -r requirements.txt` or explicitly add `flask-socketio`.

## Medium Severity

### 5. Module-Level Global State (Reliability)
`src/sejfa/monitor/monitor_routes.py` uses module-level global variables (`monitor_service`, `socketio`) set by `create_monitor_blueprint`. This creates temporal coupling and makes testing fragile, preventing concurrent test execution or multiple app instances.
**Action:** Store services in `current_app.extensions` or use dependency injection properly.

### 6. Missing WebSocket Verification (Test Coverage)
The new tests in `tests/monitor/test_monitor_routes.py` cover REST endpoints but do not verify WebSocket event emissions. This leaves a critical part of the functionality untested.
**Action:** Add tests using `socketio.test_client(app)` to verify `state_update` events are emitted.

## Low Severity

### 7. Deprecated datetime.utcnow() (Correctness)
Both `src/sejfa/monitor/monitor_routes.py` and `src/sejfa/monitor/monitor_service.py` use `datetime.utcnow()`, which is deprecated in Python 3.12.
**Action:** Replace with `datetime.now(timezone.utc)`.
