# PR Review Findings

## Critical Severity

### 1. Broken Authentication Logic (Security)
The `AdminAuthService.validate_session_token` method in `src/sejfa/core/admin_auth.py` insecurely validates tokens by only checking if they start with `"token_"`. This allows attackers to bypass authentication by providing any string with that prefix.
**Action:** Implement proper token validation (e.g., using a secure store or JWT signature verification).

### 2. Missing Authentication on Monitor Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/reset`, `/task`) in `src/sejfa/monitor/monitor_routes.py` are publicly accessible without any authentication. This allows unauthorized users to manipulate the workflow state.
**Action:** Apply the `@require_admin_token` decorator to all monitoring endpoints.

### 3. Stored XSS in Dashboard (Security)
The `monitor.html` file renders `event.message` using `innerHTML` (line 706) without sanitization. Since the state update endpoint is unauthenticated, an attacker can inject malicious scripts that execute in the dashboard viewer's browser.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

## High Severity

### 4. Hardcoded Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`username="admin"`, `password="admin123"`). This is highly insecure for production.
**Action:** Move credentials to environment variables or a secure database and use strong password hashing (e.g., bcrypt).

### 5. Hardcoded Application Secret (Security)
The `app.secret_key` is hardcoded to `"dev-secret-key"` in `app.py`. This compromises session security.
**Action:** Load `SECRET_KEY` from environment variables and fail if missing in production.

### 6. Missing CSRF Protection (Security)
The application lacks global Cross-Site Request Forgery (CSRF) protection. Forms (like `manage_subscribers`) are vulnerable to CSRF attacks.
**Action:** Initialize `Flask-WTF`'s `CSRFProtect` in `app.py` and ensure all forms include the CSRF token.

## Medium Severity

### 7. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` and `allow_unsafe_werkzeug=True`. This exposes sensitive debugging info and is unsafe for production.
**Action:** Use environment variables to control debug mode and disable it by default.

### 8. Race Conditions in MonitorService (Reliability)
The `MonitorService.update_node` method modifies shared state (`self.nodes`, `self.event_log`) without locking. In a threaded environment (default for Flask/SocketIO), this can lead to data corruption.
**Action:** Use `threading.Lock` to synchronize access to shared resources in `MonitorService`.
