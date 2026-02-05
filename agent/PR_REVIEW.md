# PR Review Findings

## High Severity

### 1. Missing Dependency (Configuration)
The `tests/monitor/test_monitor_routes.py` and `src/sejfa/monitor/monitor_routes.py` modules import `flask_socketio`, but this package is not listed in `requirements.txt`. This will cause immediate runtime errors in production and CI environments.
**Action:** Add `flask-socketio` (and `python-dotenv` if used) to `requirements.txt`.

### 2. Ineffective Test Coverage (Reliability/Correctness)
Tests in `tests/monitor/test_monitor_routes.py` (specifically `test_update_state_endpoint_exists`) assert that `POST /api/monitor/state` returns 200, 400, or 500. This assertion is overly broad, masking potential crashes (500) or validation errors (400), rendering the test useless for actual verification.
**Action:** Update the test to assert specific status codes (e.g., 200 for valid input, 400 for invalid input) and verify the response content or side effects.

### 3. Testing Non-Existent Endpoints (Correctness)
Tests `test_health_check_endpoint_exists` and `test_metrics_endpoint_exists` verify that `/api/monitor/health` and `/api/monitor/metrics` return 404 (or 200). Since these endpoints are missing from `src/sejfa/monitor/monitor_routes.py`, the tests pass by confirming they do NOT exist, creating a false sense of coverage.
**Action:** Either implement the endpoints if required or remove the meaningless tests. If testing 404 handling is intended, rename the test to reflect that (e.g., `test_unknown_route_returns_404`).

## Medium Severity

### 4. Global State Dependency (Testability/Design)
`src/sejfa/monitor/monitor_routes.py` uses global variables (`monitor_service`, `socketio`) for dependency injection. This makes the code thread-unsafe and difficult to test reliably, as state leaks between tests and parallel execution is compromised.
**Action:** Refactor `create_monitor_blueprint` to pass dependencies via `current_app` context or use a closure-based blueprint factory properly (avoiding globals).

### 5. Task/PR Mismatch (Documentation)
The PR title "GE-35 - Backend TEST (Expense Tracker)" and description suggest ExpenseTracker testing, but the actual changes are solely monitor tests. This violates the Single Responsibility Principle for PRs and misleads reviewers about the scope of changes.
**Action:** Update the PR title/description to accurately reflect the changes (e.g., "Add Monitor Route Tests") or include the missing ExpenseTracker tests if intended.

## Low Severity

### 6. Missing Type Hints (Readability)
The `create_monitor_blueprint` function signature in `src/sejfa/monitor/monitor_routes.py` lacks type hints for `service` and `socket_io`, reducing code clarity and tooling support.
**Action:** Add type hints (e.g., `service: MonitorService`, `socket_io: SocketIO`) to the function signature.
