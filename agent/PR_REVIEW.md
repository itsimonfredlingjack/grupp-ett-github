# PR Review Findings

## Critical Severity

### 1. Unintended Deletion of Monitoring Hooks (Regression)
The PR deletes `.claude/hooks/monitor_client.py` and `.claude/hooks/monitor_hook.py`, and removes integration from `stop-hook.py`. This contradicts the PR description ("Integrate Ralph Loop with real-time monitor dashboard") and breaks the core functionality of tracking agent state from within the loop. The bash wrapper `claude-monitor-wrapper.sh` is an inferior substitute that lacks context awareness (e.g., specific tools used).
**Action:** Restore the Python hooks and `stop-hook.py` integration to ensure robust monitoring.

## High Severity

### 2. Unauthenticated Monitoring Endpoints (Security)
The new API endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are publicly accessible without authentication. This allows unauthorized users to modify the dashboard state or reset monitoring data.
**Action:** Implement authentication (e.g., API key or token verification) for all state-modifying endpoints.

### 3. Missing CSRF Exemption for API (Security)
The monitoring API endpoints (`POST /api/monitor/*`) are not marked as exempt from CSRF protection. Once global CSRF protection is enabled (as required for other modules), these endpoints will fail because clients do not send CSRF tokens.
**Action:** Apply `@csrf.exempt` to these endpoints (contingent on adding API authentication) or implement token handling.

## Medium Severity

### 4. Reliance on Global Variables (Design)
`monitor_routes.py` relies on `global monitor_service` and `global socketio` for dependency injection. This pattern causes issues with test isolation, thread safety, and code maintainability.
**Action:** Refactor to use `current_app.extensions` or a proper factory pattern for dependency injection.

### 5. Fragile Bash Wrapper Implementation (Reliability)
The `claude-monitor-wrapper.sh` script relies on regex matching of standard output to determine the current node. This is brittle and may misclassify states compared to the direct tool-use hooks that were deleted.
**Action:** Rely on the restored Python hooks for state tracking, or strictly define the output patterns and add tests for the bash wrapper.

### 6. Code Duplication (Code Quality)
In `src/sejfa/monitor/monitor_routes.py`, the line `data = request.get_json(silent=True)` is duplicated in the `update_state` function.
**Action:** Remove the redundant line.
