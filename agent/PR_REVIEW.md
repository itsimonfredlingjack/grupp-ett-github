# PR Review Findings

## High Severity

### 1. Thread Safety Issue in MonitorService (Reliability)
The `MonitorService` class manages state using in-memory dictionaries (`self.nodes`, `self.event_log`) without any locking mechanism. In a production environment with multiple workers (e.g., gunicorn), this will lead to a "split-brain" scenario where each worker maintains its own isolated state, causing inconsistent monitoring data.
**Action:** Use a persistent backing store (e.g., Redis) or a singleton pattern compatible with the deployment architecture.

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are completely unauthenticated. This allows any actor with network access to inject false events, reset the monitoring state, or disrupt the agentic loop visualization.
**Action:** Implement authentication for these endpoints, such as requiring an API key or using the existing `AdminAuthService`.

### 3. Missing Global CSRF Protection (Security)
The application lacks global Cross-Site Request Forgery (CSRF) protection. While some forms might be protected manually, `app.py` does not initialize `CSRFProtect` from `Flask-WTF`, leaving the application vulnerable to CSRF attacks.
**Action:** Initialize `CSRFProtect(app)` in `app.py` to enable global protection.

## Medium Severity

### 4. Deprecated Datetime Usage (Maintainability)
The `MonitorService` uses `datetime.utcnow()`, which is deprecated in Python 3.12+ and scheduled for removal. This will cause future compatibility issues.
**Action:** Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.

## Low Severity

### 5. Unsafe Application Configuration (Security)
The `app.py` file enables `debug=True` and `allow_unsafe_werkzeug=True` in the `if __name__ == "__main__":` block. While this block is guarded, it poses a risk if the application is executed directly in a production environment.
**Action:** Ensure these settings are disabled in production environments, preferably by loading them from environment variables (e.g., `FLASK_DEBUG`).
