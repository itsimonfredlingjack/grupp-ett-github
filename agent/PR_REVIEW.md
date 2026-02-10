# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username`: 'admin', `password`: 'admin123'). This creates a critical security vulnerability if deployed.
**Action:** Replace hardcoded credentials with environment variables or a database-backed authentication system.

### 2. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization in the `updateEventLog` function. This allows an attacker to inject malicious scripts via the monitoring API.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering.

## High Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 4. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 5. Hardcoded Secret Key (Security)
The application uses a hardcoded secret key (`"dev-secret-key"`) in `app.py`. The key should be loaded from environment variables using `python-dotenv`.
**Action:** Use `python-dotenv` to load the secret key from `.env` and default to a random string if not found.

## Medium Severity

### 6. MonitorService Thread Safety Issues (Reliability)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` is not thread-safe. The `update_node` method modifies `self.nodes` and `self.event_log` without locking, which can lead to race conditions in a multi-threaded environment.
**Action:** Add locking mechanisms (e.g., `threading.Lock`) to critical sections or use thread-safe data structures.

### 7. Deprecated datetime.utcnow() Usage (Reliability)
The `MonitorService` uses `datetime.utcnow()`, which is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace `datetime.utcnow()` with `datetime.now(timezone.utc)`.

## Low Severity

### 8. Missing Dependency: python-dotenv (Maintainability)
The application relies on environment variables for configuration (e.g., `SECRET_KEY`), but `python-dotenv` is missing from `requirements.txt`.
**Action:** Add `python-dotenv` to `requirements.txt` to ensure environment variables are loaded correctly in development.
