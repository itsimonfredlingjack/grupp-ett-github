# PR Review Findings

## Critical Severity

### 1. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization (Line 698). An attacker can inject malicious scripts via the `message` field in the monitoring API, executing code in the browser of any user viewing the dashboard.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` uses hardcoded credentials (`username: "admin"`, `password: "[REDACTED]"`). This allows anyone with access to the source code or who guesses these common credentials to gain admin access.
**Action:** Move credentials to environment variables or a secure database, and use a strong hashing algorithm.

## High Severity

### 3. Weak Secret Key Configuration (Security)
The application `SECRET_KEY` in `app.py` falls back to a hardcoded "dev-secret-key" if the environment variable is unset. This compromises session security and cryptographic signatures in production.
**Action:** Enforce loading `SECRET_KEY` from environment variables and fail startup if not present in production.

### 4. In-Memory State in Multi-Worker Environment (Reliability)
The `MonitorService` relies on in-memory dictionaries (`self.nodes`, `self.event_log`) to track state. In a production environment running with `gunicorn` and multiple workers, this state will be fragmented across processes, leading to inconsistent monitoring data (split-brain).
**Action:** Use a shared data store (e.g., Redis or a database) for `MonitorService` state, or configure `gunicorn` to use a single worker with threads (though thread safety must still be addressed).

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are completely unauthenticated. This allows any network user to inject false events, reset the dashboard, or disrupt the monitoring service.
**Action:** Implement authentication for these endpoints, such as requiring an API key or a shared secret header, and validate it in a `before_request` handler or decorator.

### 6. Missing CSRF Protection (Security)
The News Flash subscription form in `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html` lacks a CSRF token. This makes the application vulnerable to Cross-Site Request Forgery attacks, where an attacker could trick a user into submitting the form without their consent.
**Action:** Implement CSRF protection using `Flask-WTF` or manually verify CSRF tokens on form submission.

## Medium Severity

### 7. API Schema Mismatch (Correctness)
There is a schema mismatch between the client and server implementations for task updates:
- `monitor_client.py` sends `action` ("start", "complete") and `task_id`.
- `monitor_routes.py` expects `status` ("idle", "running", "completed") and ignores `action` and `task_id`.
This prevents the dashboard from correctly tracking task start/completion events.
**Action:** Update `monitor_routes.py` to handle the `action` field and map "start"/"complete" to appropriate status updates, or update `monitor_client.py` to match the server schema.
