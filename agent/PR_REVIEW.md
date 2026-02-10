# PR Review Findings

## Critical Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 2. Missing Implementation in Active Module (Correctness)
The active application (registered in `app.py`) uses the `newsflash` module (`src/sejfa/newsflash`), but the module does not have updated styles. `src/sejfa/newsflash/presentation/static/css/style.css` still contains the old color scheme (`#0a0e1a`, `#3b82f6`) instead of the new one (`#1a1d29` -> `#0f1117`).
**Action:** Update the CSS variables to match the new design system.

## High Severity

### 3. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 4. Hardcoded Secret Key (Security)
`app.py` sets `app.secret_key = "dev-secret-key"` without a fallback to environment variables. This compromises session security in production.
**Action:** Update `app.py` to use `os.environ.get("SECRET_KEY")` and fail or fallback securely.

### 5. Verify Dependency Pinning (Reliability)
Ensure `python-dotenv` and `Flask-WTF` are pinned to stable versions in `requirements.txt` (e.g., `>=1.0.0`) to prevent future breaking changes, as they are utilized by the application/tests.
**Action:** Add missing dependencies to `requirements.txt`.

## Medium Severity

### 6. Thread Safety in MonitorService (Reliability)
`MonitorService` in `src/sejfa/monitor/monitor_service.py` modifies shared state (`self.nodes`, `self.event_log`) without locking. This is not thread-safe and may cause race conditions in a multi-threaded environment.
**Action:** Add `threading.Lock` to protect shared state modifications.

## Low Severity

### 7. Deprecated datetime.utcnow (Maintainability)
`MonitorService` and `MonitorRoutes` use `datetime.utcnow()`, which is deprecated in Python 3.12.
**Action:** Replace with `datetime.now(datetime.timezone.utc)` or similar.
