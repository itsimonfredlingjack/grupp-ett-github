## Critical Severity

### 1. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization. An attacker can inject malicious scripts via the `message` field in the monitoring API, executing code in the browser of any user viewing the dashboard.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` uses hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code or who guesses these common credentials to gain admin access.
**Action:** Move credentials to environment variables or a secure database, and use a strong hashing algorithm.

## High Severity

### 3. In-Memory State in Multi-Worker Environment (Reliability)
The `MonitorService` relies on in-memory dictionaries (`self.nodes`, `self.event_log`) to track state. In a production environment running with `gunicorn` and multiple workers, this state will be fragmented across processes, leading to inconsistent monitoring data (split-brain).
**Action:** Use a shared data store (e.g., Redis or a database) for `MonitorService` state, or configure `gunicorn` to use a single worker with threads (though thread safety must still be addressed).

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are completely unauthenticated. This allows any network user to inject false events, reset the dashboard, or disrupt the monitoring service.
**Action:** Implement authentication for these endpoints, such as requiring an API key or a shared secret header, and validate it in a `before_request` handler or decorator.

### 5. Missing CSRF Protection (Security)
The News Flash subscription form in `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html` lacks a CSRF token. This makes the application vulnerable to Cross-Site Request Forgery attacks, where an attacker could trick a user into submitting the form without their consent.
**Action:** Implement CSRF protection using `Flask-WTF` or manually verify CSRF tokens on form submission.

## Medium Severity

### 6. API Schema Mismatch (Correctness)
There is a schema mismatch between the client and server implementations for task updates:
- `monitor_client.py` sends `action` ("start", "complete") and `task_id`.
- `monitor_routes.py` expects `status` ("idle", "running", "completed") and ignores `action` and `task_id`.
This prevents the dashboard from correctly tracking task start/completion events.
**Action:** Update `monitor_routes.py` to handle the `action` field and map "start"/"complete" to appropriate status updates, or update `monitor_client.py` to send the expected `status` field.

### 7. Missing Tests for Monitoring Module (Testing)
The monitoring module (`src/sejfa/monitor/`) lacks unit and integration tests. The test file `tests/monitor/test_monitor_routes.py` (referenced in previous reviews) does not exist in the repository, leaving the critical monitoring functionality unverified.
**Action:** Create comprehensive tests for `MonitorService` and `monitor_routes.py`, covering all endpoints and logic.

## Low Severity

### 8. Use of Global Variables (Maintainability)
The `monitor_routes.py` module relies on module-level global variables (`monitor_service`, `socketio`) which are populated via `create_monitor_blueprint`. This makes testing difficult (requiring global state management) and is not thread-safe if the module is reloaded.
**Action:** Register these services on `current_app` or use the `g` object to ensure proper application context and thread safety.
