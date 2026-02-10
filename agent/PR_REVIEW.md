# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The file `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`"username": "admin", "password": "[REDACTED]"`). This is a critical security vulnerability that allows trivial unauthorized access.
**Action:** Remove hardcoded credentials. Use environment variables or a secure secret management solution.

## High Severity

### 2. Missing Test Files (Correctness)
Tests for `MonitorService` and `MonitorRoutes` are missing from the codebase (`tests/monitor/` does not exist). This leaves new functionality unverified.
**Action:** Restore the missing test files or revert the changes if the tests are not ready.

### 3. Authentication Bypass (Security)
Monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`, `/reset`) are unprotected. Anyone with network access can manipulate the monitoring state or reset it.
**Action:** Implement authentication (e.g., `@login_required` or API key validation) for all sensitive monitoring endpoints.

### 4. Stored XSS Vulnerability (Security)
The file `static/monitor.html` uses `innerHTML` to render event messages without sanitization. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

## Medium Severity

### 5. Inconsistent JSON Error Handling (Reliability)
The code in `src/sejfa/monitor/monitor_routes.py` uses `request.get_json()` without `silent=True` or explicit error handling. If an invalid JSON payload is sent, Flask will raise a 400 Bad Request, which may not align with the expected API error format for automated clients.
**Action:** Use `request.get_json(silent=True)` and handle `None` return value to provide a consistent error response structure.

### 6. Global State Dependency (Reliability)
The `src/sejfa/monitor/monitor_routes.py` module relies on module-level global variables (`monitor_service`, `socketio`) which are injected via `create_monitor_blueprint`. This pattern makes testing difficult and can cause race conditions in a multi-worker environment (e.g., gunicorn).
**Action:** Refactor to use a proper dependency injection pattern or Flask's `current_app` context to store service instances.
