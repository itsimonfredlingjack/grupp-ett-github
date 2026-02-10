# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code or knowledge of default credentials to gain administrative access.
**Action:** Replace hardcoded credentials with environment variables (e.g., `ADMIN_USERNAME`, `ADMIN_PASSWORD`) and use a secure hashing algorithm for passwords.

### 2. Unprotected Monitoring Endpoints (Correctness)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `POST /api/monitor/reset`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or manipulate task status.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key mechanism.

## High Severity

### 3. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization: `eventItem.innerHTML = ... ${event.message} ...`. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Sanitize `event.message` before rendering it, or use `textContent` instead of `innerHTML`.

### 4. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a significant security risk if deployed to production (e.g., arbitrary code execution via the debugger).
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 5. Hardcoded Secret Key (Security)
The application `SECRET_KEY` in `app.py` falls back to "dev-secret-key" if the environment variable is unset. Using a hardcoded secret key compromises session security and CSRF protection.
**Action:** Require `SECRET_KEY` to be set via environment variables in production and fail startup if missing.

## Medium Severity

### 6. Missing Data Persistence in News Flash (Correctness)
The `SubscriptionService` in `src/sejfa/newsflash/business/subscription_service.py` validates inputs but does not persist the subscription data (e.g., to a database or file). This results in data loss as subscriptions are processed but not stored.
**Action:** Implement a persistence layer (e.g., `SubscriptionRepository`) to store validated subscriptions.

### 7. Thread Safety Issues in Monitoring Service (Reliability)
The `MonitorService` and `SubscriberService` rely on unprotected in-memory dictionaries (`self.nodes`, `_subscribers`). In a multi-threaded or multi-worker environment (like gunicorn with multiple workers), this leads to race conditions and "split-brain" state issues.
**Action:** Use a thread-safe data store (e.g., Redis, database) or implement locking mechanisms if running in a single process.

### 8. Outdated CSS Color Scheme (Correctness)
The file `src/sejfa/newsflash/presentation/static/css/style.css` uses the outdated color code `#0a0e1a` instead of the new design system's `#1a1d29`. This results in visual inconsistencies with the rest of the application.
**Action:** Update the CSS to use the correct color code `#1a1d29` as per the design system.
