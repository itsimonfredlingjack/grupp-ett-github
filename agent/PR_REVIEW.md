## Critical Severity

### 1. Split-Brain Task State (Process)
The repository contains both `docs/CURRENT_TASK.md` (3333 bytes) and `CURRENT_TASK.md` (2223 bytes), creating conflicting sources of truth for the active task. This violates the "Single Source of Truth" principle and causes confusion for agents.
**Action:** Consolidate task state into the root `CURRENT_TASK.md` and delete `docs/CURRENT_TASK.md`.

### 2. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_` (e.g., `token_fake`), allowing complete authentication bypass for critical admin actions.
**Action:** Implement proper session validation (e.g., check against a stored session store or use JWT).

### 3. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders WebSocket event messages using `innerHTML` without sanitization. An attacker could inject malicious scripts via crafted event messages, executing arbitrary code in the context of the monitoring dashboard.
**Action:** Use `textContent` or sanitize the input before rendering.

## High Severity

### 4. Global CSRF Protection Missing (Security)
The Flask application (`app.py`) lacks global Cross-Site Request Forgery (CSRF) protection, leaving state-changing endpoints (e.g., `/admin/subscribers`, `/api/monitor/state`) vulnerable to CSRF attacks.
**Action:** Install `flask-wtf` and enable `CSRFProtect(app)`.

### 5. Hardcoded Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin` / `admin123`) and defaults to insecure values if environment variables are missing. This is a significant security risk for production deployments.
**Action:** Remove hardcoded credentials and enforce environment variable configuration (e.g., raise an error if `ADMIN_PASSWORD` is not set).

### 6. Race Conditions in Monitor Service (Reliability)
The `MonitorService` relies on unprotected in-memory dictionaries (`nodes`, `event_log`) without thread-safe locking. In a threaded environment (e.g., Flask development server or Gunicorn with threads), concurrent requests can corrupt the internal state.
**Action:** Implement thread-safe locking (e.g., `threading.RLock`) for state modifications.

## Medium Severity

### 7. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `/reset`, `/task`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or manipulate task information.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 8. Missing Dependency: python-dotenv (Reliability)
The `scripts/preflight.sh` script relies on `python-dotenv` (via `from dotenv import load_dotenv`), but it is missing from `requirements.txt`. This causes the preflight check to fail in clean environments.
**Action:** Add `python-dotenv` to `requirements.txt`.
