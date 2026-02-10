# PR Review Findings

## Critical Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) lack authentication. This allows any network user to inject false events or reset the dashboard state. The tests in `tests/monitor/test_monitor_routes.py` confirm this insecure behavior by succeeding without authentication.
**Action:** Implement authentication for these endpoints, verifying `Authorization: Bearer <MONITOR_API_KEY>`.

### 2. Broken CI Configuration (Reliability)
The `.github/workflows/ci_branch.yml` workflow installs dependencies manually (`pip install pytest ... flask`) instead of using `pip install -r requirements.txt`. This omits `flask-socketio`, causing `tests/monitor/test_monitor_routes.py` to fail in CI with `ImportError`.
**Action:** Update the workflow to `pip install -r requirements.txt`.

## Medium Severity

### 3. Deprecated datetime.utcnow() (Reliability)
The `monitor_routes.py` file uses `datetime.utcnow()`, which is deprecated and scheduled for removal in future Python versions.
**Action:** Replace with `datetime.now(datetime.timezone.utc)` (requires `from datetime import timezone`).

### 4. Missing Negative Test Cases (Test Coverage)
The added tests cover only the happy path and invalid JSON, but do not test authentication failures (which should be implemented).
**Action:** Add test cases to verify that requests without a valid token are rejected with 401 Unauthorized.

## Low Severity

### 5. Context Loss in CURRENT_TASK.md (Process)
The PR truncates `CURRENT_TASK.md` to a verification checklist, removing the mandatory agent instructions. This might impact future agent context.
**Action:** Ensure critical instructions are preserved or restored.
