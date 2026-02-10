# PR Review Findings

## Medium Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/state`, `/reset`) are unauthenticated, allowing any network user to modify the monitoring state.
**Action:** Implement authentication (e.g., API key or AdminAuthService) for these endpoints.

## Low Severity

### 2. Unsafe Application Configuration (Security)
The `app.py` file enables `debug=True` and `allow_unsafe_werkzeug=True` in the main execution block. This is unsafe for production deployments.
**Action:** Use environment variables (e.g., `FLASK_DEBUG`) to control these settings.
