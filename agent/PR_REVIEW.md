# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code to gain administrative access.
**Action:** Replace with environment variables and use secure password hashing.

### 2. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization: `eventItem.innerHTML = ... ${event.message} ...`. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Sanitize `event.message` before rendering it, or use `textContent` instead of `innerHTML`.

### 3. Missing Data Persistence in News Flash (Correctness)
The subscription route in `src/sejfa/newsflash/presentation/routes.py` processes subscriptions via `SubscriptionService.process_subscription`, which validates but does not persist the data. Validated subscriptions are lost immediately, causing a critical functional failure.
**Action:** Implement persistence (e.g., database or file storage) for subscriptions.

## High Severity

### 4. Weak Authentication Validation (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` validates session tokens using `token.startswith("token_")`. This allows an attacker to bypass authentication by sending any token starting with `token_` (e.g., `token_hacker`).
**Action:** Implement proper token validation, such as checking against a stored list of valid session tokens or using signed JWTs.

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or manipulate task status.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key mechanism.

### 6. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a significant security risk if deployed to production (e.g., arbitrary code execution via the debugger).
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

## Medium Severity

### 7. Hardcoded Secret Key (Security)
The application `SECRET_KEY` in `app.py` falls back to "dev-secret-key" if the environment variable is unset. Using a hardcoded secret key compromises session security.
**Action:** Enforce loading `SECRET_KEY` from environment variables; fail if missing in production.

### 8. In-Memory Persistence & Split-Brain (Reliability)
`MonitorService` relies on in-memory state. In a multi-worker deployment (e.g., Gunicorn), this causes a "split-brain" scenario where workers maintain independent states, leading to inconsistent monitoring data.
**Action:** Use an external store (e.g., Redis, Database) for shared state.
