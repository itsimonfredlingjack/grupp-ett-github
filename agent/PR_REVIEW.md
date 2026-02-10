# Automated PR Review

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
`src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This is a critical security vulnerability that allows unauthorized access.
**Action:** Move credentials to environment variables or a secure database.

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## High Severity

### 3. Stored XSS in Monitor Dashboard (Security)
`static/monitor.html` renders `event.message` using `innerHTML` without sanitization. This allows malicious scripts to be injected via monitoring events and executed in the dashboard context.
**Action:** Sanitize input before rendering or use `textContent` instead of `innerHTML`.

### 4. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 5. Hardcoded Secret Key (Security)
`app.py` sets `app.secret_key = "dev-secret-key"` without a fallback to environment variables. This compromises session security in production.
**Action:** Update `app.py` to use `os.environ.get("SECRET_KEY")` and fail or fallback securely.

### 6. Missing Dependency: python-dotenv (Reliability)
`python-dotenv` is used in `src/sejfa/integrations/jira_client.py` and listed in `pyproject.toml`, but is missing from `requirements.txt`. This can cause runtime errors in environments relying on `requirements.txt`.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.

## Medium Severity

### 7. Thread Safety in MonitorService (Reliability)
`MonitorService` in `src/sejfa/monitor/monitor_service.py` modifies shared state (`self.nodes`, `self.event_log`) without locking. This is not thread-safe and may cause race conditions in a multi-threaded environment.
**Action:** Add `threading.Lock` to protect shared state modifications.

### 8. Outdated CSS Variables (Correctness)
`src/sejfa/newsflash/presentation/static/css/style.css` uses the old color scheme (`#0a0e1a`) instead of the new design system (`#1a1d29`).
**Action:** Update the CSS variables to match the new design system.
