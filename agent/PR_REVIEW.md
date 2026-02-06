# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username`: "admin", `password`: "admin123"). This allows anyone with access to the source code to gain administrative access.
**Action:** Remove hardcoded credentials. Use a secure storage mechanism (e.g., database with hashed passwords) or environment variables for the MVP.

## High Severity

### 2. Authentication Bypass in Token Validation (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` only checks if the token starts with "token_". This allows an attacker to bypass authentication by providing any string with this prefix (e.g., "token_fake").
**Action:** Implement proper session management or token verification (e.g., JWT or server-side session store).

### 3. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` directly using `innerHTML` without sanitization. If an attacker can inject a malicious message into the event log (e.g., via the unprotected monitoring endpoints), it will execute in the browser of any user viewing the dashboard.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering.

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 5. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. Additionally, `app.secret_key` is hardcoded to "dev-secret-key". While acceptable for local development, these settings pose a risk if deployed to production.
**Action:** Ensure these settings are disabled or securely configured in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`, `SECRET_KEY`).
