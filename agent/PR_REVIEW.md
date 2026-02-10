# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` uses hardcoded credentials (`admin`/`admin123`). This allows unauthorized access if the service is exposed.
**Action:** Replace hardcoded credentials with environment variables or a secure database storage.

## High Severity

### 2. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file uses `innerHTML` to render `event.message` and `event.node` without sanitization. This allows malicious scripts to be executed in the dashboard context.
**Action:** Use `textContent` or a sanitization library when rendering untrusted input.

### 3. Weak Token Validation (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_`, allowing authentication bypass.
**Action:** Implement proper token validation (e.g., JWT signature verification or server-side session storage).

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated, allowing anyone to inject fake events.
**Action:** Implement authentication for these endpoints.

## Medium Severity

### 5. Unsafe Application Configuration (Security)
The `app.py` file enables `debug=True` and `allow_unsafe_werkzeug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production without a proper WSGI server.
**Action:** Ensure these settings are disabled in production environments.
