# PR Review Findings

## Critical Severity

### 1. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method in `src/sejfa/core/admin_auth.py` accepts any token starting with `token_`. This allows complete bypass of authentication checks.
**Action:** Implement proper token validation (e.g., using a secure random token store or JWT).

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` class contains hardcoded credentials (`username: "admin"`, `password: "[REDACTED]"`). This is a critical security vulnerability.
**Action:** Remove hardcoded credentials. Use environment variables or a secure database for credential storage.

### 3. Data Loss in News Flash Subscription (Correctness)
The `subscribe_confirm` route in `src/sejfa/newsflash/presentation/routes.py` validates input but fails to persist the subscription data. All user subscriptions are silently discarded.
**Action:** Integrate `SubscriberService` or a database to persist validated subscriptions.

## High Severity

### 4. Split-Brain State in Multi-Worker Deployment (Reliability)
The `MonitorService` stores state in-memory, but the Docker deployment uses `gunicorn` with 4 workers. This causes a "split-brain" state where dashboard clients only see updates handled by the specific worker they are connected to.
**Action:** Use a shared state store (e.g., Redis) or configure gunicorn to use a single worker with async support.

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or inject XSS payloads.
**Action:** Implement authentication for these endpoints.

### 6. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization. This allows attackers to execute arbitrary JavaScript in the dashboard context via injected events.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input.

## Medium Severity

### 7. Hardcoded Secret Key (Security)
The application uses a hardcoded `SECRET_KEY` in `app.py`. This compromises session security if deployed to production.
**Action:** Load `SECRET_KEY` from environment variables and fail if not set in production.

### 8. Missing CSRF Protection (Security)
The application lacks global CSRF protection (e.g., `Flask-WTF`'s `CSRFProtect`). The subscription form in `subscribe.html` does not include a CSRF token, making it vulnerable to Cross-Site Request Forgery.
**Action:** Enable global CSRF protection and include CSRF tokens in all forms.
