# PR Review Findings

## Critical Severity

### 1. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method in `src/sejfa/core/admin_auth.py` accepts any token starting with `token_` (e.g., `Bearer token_hack`). This allows attackers to bypass authentication entirely without knowing the password.
**Action:** Implement proper token validation (e.g., store active tokens in a database or use signed JWTs).

### 2. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username`: 'admin', `password`: '******'). This is a severe security risk if deployed.
**Action:** Replace with environment variables or a database-backed solution.

## High Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints (e.g., API key or token).

### 4. Stored XSS Vulnerability (Security)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` stores unsanitized `message` content. The frontend (`static/monitor.html`) renders this using `innerHTML`, creating a Stored Cross-Site Scripting (XSS) vulnerability.
**Action:** Sanitize all inputs in `MonitorService` or ensure the frontend uses `textContent` / safe rendering methods.

### 5. Missing CSRF Protection (Security)
Global CSRF protection is not enabled in `app.py`. The application (including the News Flash subscription form) is vulnerable to Cross-Site Request Forgery attacks.
**Action:** Enable `CSRFProtect` from `flask-wtf` and ensure all forms include CSRF tokens.

### 6. Insecure Secret Key (Security)
`app.py` uses a hardcoded fallback `SECRET_KEY` ("******"). If deployed without an environment variable, session cookies can be forged.
**Action:** Enforce loading `SECRET_KEY` from environment variables in production and fail if not set.

## Medium Severity

### 7. Thread Safety Issues (Reliability)
`MonitorService` and `SubscriberService` rely on unprotected in-memory dictionaries (`self.nodes`, `_subscribers`). In a multi-worker environment (like Gunicorn), this leads to race conditions and data inconsistency.
**Action:** Use a thread-safe data store (Redis/Database) or add `threading.Lock` for synchronization.

### 8. Deprecated DateTime Usage (Reliability)
`src/sejfa/monitor/monitor_service.py` uses `datetime.utcnow()`, which is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace with `datetime.now(datetime.UTC)` to ensure future compatibility.
