## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code or knowledge of default credentials to gain administrative access.
**Action:** Replace hardcoded credentials with environment variables (e.g., `ADMIN_USERNAME`, `ADMIN_PASSWORD`) and use a secure hashing algorithm for passwords.

### 2. Weak Authentication Validation (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` validates session tokens using `token.startswith("token_")`. This allows an attacker to bypass authentication by sending any token starting with `token_` (e.g., `token_hacker`).
**Action:** Implement proper token validation, such as checking against a stored list of valid session tokens or using signed JWTs.

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or manipulate task status.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key mechanism.

## High Severity

### 4. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization: `eventItem.innerHTML = ... ${event.message} ...`. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Sanitize `event.message` before rendering it, or use `textContent` instead of `innerHTML`.

### 5. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a significant security risk if deployed to production (e.g., arbitrary code execution via the debugger).
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 6. Hardcoded Secret Key (Security)
The application `SECRET_KEY` in `app.py` falls back to "dev-secret-key" if the environment variable is unset. Using a hardcoded secret key compromises session security and CSRF protection.
**Action:** Require `SECRET_KEY` to be set via environment variables in production and fail startup if missing.

### 7. Global CSRF Protection Missing (Security)
The application lacks global CSRF protection. `app.py` does not initialize `CSRFProtect` from `Flask-WTF`, and forms like `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html` do not include CSRF tokens.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect(app)` in `app.py`, and add `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` to all forms.

## Medium Severity

### 8. Broken Task Monitoring API Contract (Correctness)
There is an API incompatibility between `monitor_client.py` and `monitor_routes.py`. The client sends `action="start"` and `task_id`, but the server endpoint `/api/monitor/task` expects `status` and `title`. This results in tasks starting with an empty status, breaking the monitoring visualization.
**Action:** Update `monitor_client.py` to send `status="running"` or update `monitor_routes.py` to map `action="start"` to `status="running"`.
