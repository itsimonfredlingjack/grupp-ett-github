## Critical Severity

### 1. CI Dependency Regression (Reliability)
The `.github/workflows/ci_branch.yml` file removes `pip install -r requirements.txt` and replaces it with `pip install ... flask`. This causes tests to fail with `ImportError` because `flask-socketio` and other dependencies are not installed.
**Action:** Restore `pip install -r requirements.txt` in the workflow.

### 2. Loop Protection Regression (Reliability)
The PR reverts critical loop protection safeguards in `.github/workflows/jules_review.yml` and `.github/workflows/self_healing.yml` (e.g., removing the `[skip-jules-review]` check). This creates a risk of infinite CI loops.
**Action:** Revert changes to these workflow files or restore the loop protection logic.

### 3. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code or knowledge of default credentials to gain administrative access.
**Action:** Replace hardcoded credentials with environment variables (e.g., `ADMIN_USERNAME`, `ADMIN_PASSWORD`) and use a secure hashing algorithm for passwords.

### 4. Weak Authentication Validation (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` validates session tokens using `token.startswith("token_")`. This allows an attacker to bypass authentication by sending any token starting with `token_` (e.g., `token_hacker`).
**Action:** Implement proper token validation, such as checking against a stored list of valid session tokens or using signed JWTs.

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or manipulate task status.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key mechanism.

## High Severity

### 6. Test Isolation Leak (Reliability)
The `stop_hook` fixture in `tests/agent/test_stop_hook.py` modifies `sys.modules["monitor_client"]` without cleaning it up. This pollutes the global module state for all subsequent tests in the same process, potentially causing false positives or masking bugs in other test modules.
**Action:** Use `unittest.mock.patch.dict(sys.modules, ...)` or manually restore `sys.modules` in a `yield` fixture pattern to ensure clean test isolation.

### 7. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization: `eventItem.innerHTML = ... ${event.message} ...`. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Sanitize `event.message` before rendering it, or use `textContent` instead of `innerHTML`.

## Medium Severity

### 8. Missing WebSocket Test Coverage (Coverage)
The new tests in `tests/monitor/test_monitor_routes.py` cover REST endpoints but omit WebSocket event handlers (`connect`, `request_state`, `state_update`). This leaves the real-time communication layer unverified.
**Action:** Add tests using `socketio.test_client()` to verify that events are emitted correctly to connected clients.
