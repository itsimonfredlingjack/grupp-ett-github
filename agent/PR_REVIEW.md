# Automated PR Review Findings

## Critical Severity

### 1. Split-Brain Task State (Process)
The repository contains both `docs/CURRENT_TASK.md` and `CURRENT_TASK.md`, creating conflicting sources of truth for the active task. This violates the "Single Source of Truth" principle and causes confusion for agents.
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
The `AdminAuthService` uses hardcoded credentials (`admin` / `admin123`) and defaults to insecure values if environment variables are missing. The `app.py` also uses a hardcoded `secret_key` ("dev-secret-key"). This is a significant security risk for production deployments.
**Action:** Remove hardcoded credentials and enforce environment variable configuration (e.g., raise an error if `ADMIN_PASSWORD` or `SECRET_KEY` is not set).

### 6. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`, `/reset`, `/task`) are unauthenticated. This allows any network user to inject false events, reset the dashboard state, or update task info.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 7. Missing Dependency: python-dotenv (Reliability)
The `scripts/preflight.sh` script relies on `python-dotenv` to load environment variables, but it is missing from `requirements.txt`. This causes the preflight check and CI workflows relying on it to fail if the package is not pre-installed.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.

## Medium Severity

### 8. Race Conditions in Monitor Service (Reliability)
The `MonitorService` relies on unprotected in-memory dictionaries (`nodes`, `event_log`) without thread-safe locking. In a threaded environment (e.g., Flask development server or Gunicorn with threads), concurrent requests could corrupt the state or cause runtime errors.
**Action:** Use `threading.RLock` to protect access to shared state in `MonitorService`.
