# PR Review Findings

## Critical Severity

### 1. Split-Brain Task State (Process)
The repository contains both `docs/CURRENT_TASK.md` (active task GE-51) and `CURRENT_TASK.md` (previous task GE-49). This causes confusion for agents and split-brain task states.
**Action:** Consolidate task state into the root `CURRENT_TASK.md` and delete `docs/CURRENT_TASK.md`.

### 2. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_`, allowing complete authentication bypass.
**Action:** Implement proper session validation (e.g., check against a stored session store or use JWT).

### 3. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders WebSocket event messages using `innerHTML` without sanitization, allowing arbitrary script execution via crafted messages.
**Action:** Use `textContent` or sanitize the input before rendering.

## High Severity

### 4. Global CSRF Protection Missing (Security)
The Flask application (`app.py`) lacks global Cross-Site Request Forgery (CSRF) protection, leaving state-changing endpoints vulnerable.
**Action:** Install `flask-wtf` and enable `CSRFProtect(app)`.

### 5. Hardcoded Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin` / `admin123`) and defaults to insecure values if environment variables are missing.
**Action:** Remove hardcoded credentials and enforce environment variable configuration.

### 6. Race Conditions in Monitor Service (Reliability)
The `MonitorService` relies on unprotected in-memory dictionaries (`nodes`, `event_log`) without locking. This causes race conditions and data corruption under load or with multiple workers.
**Action:** Implement thread-safe locking or use an external store like Redis.

## Medium Severity

### 7. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated, allowing unauthorized updates or resets.
**Action:** Implement authentication for these endpoints.

### 8. Missing Dependency: python-dotenv (Reliability)
The `scripts/preflight.sh` script relies on `python-dotenv`, but it is missing from `requirements.txt`.
**Action:** Add `python-dotenv` to `requirements.txt`.
