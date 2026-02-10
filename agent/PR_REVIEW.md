# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username`: 'admin', `password`: '******'). This is a severe security risk if deployed.
**Action:** Replace with environment variables or a database-backed solution.

## High Severity

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints (e.g., API key or token).

### 3. Stored XSS Vulnerability (Security)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` stores unsanitized `message` content. The frontend (`static/monitor.html`) renders this using `innerHTML`, creating a Stored Cross-Site Scripting (XSS) vulnerability.
**Action:** Sanitize all inputs in `MonitorService` or ensure the frontend uses `textContent` / safe rendering methods.

### 4. Missing CSRF Protection (Security)
Global CSRF protection is not enabled in `app.py`. The application (including the News Flash subscription form) is vulnerable to Cross-Site Request Forgery attacks.
**Action:** Enable `CSRFProtect` from `flask-wtf` and ensure all forms include CSRF tokens.

### 5. Insecure Secret Key (Security)
`app.py` uses a hardcoded fallback `SECRET_KEY` ("******"). If deployed without an environment variable, session cookies can be forged.
**Action:** Enforce loading `SECRET_KEY` from environment variables in production and fail if not set.

## Medium Severity

### 6. Thread Safety Issues (Reliability)
`MonitorService` is not thread-safe. Methods like `update_node` modify shared state (`self.nodes`, `self.event_log`) without locking. In a multi-threaded environment (e.g., Gunicorn), this leads to race conditions.
**Action:** Add `threading.Lock` to `MonitorService` to synchronize access to shared resources.

### 7. Deprecated DateTime Usage (Reliability)
`src/sejfa/monitor/monitor_service.py` uses `datetime.utcnow()`, which is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace with `datetime.now(datetime.UTC)` to ensure future compatibility.

## Low Severity

### 8. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments.
