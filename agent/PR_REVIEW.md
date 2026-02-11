# Automated PR Review Findings

## Critical Severity

### 1. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_` (e.g., `token_fake`), allowing complete authentication bypass for critical admin actions.
**Action:** Implement proper session validation (e.g., check against a stored session store or use JWT).

### 2. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders WebSocket event messages using `innerHTML` without sanitization. An attacker could inject malicious scripts via crafted event messages, executing arbitrary code in the context of the monitoring dashboard.
**Action:** Use `textContent` or sanitize the input before rendering.

## High Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state, serving as a vector for the Stored XSS vulnerability.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 4. Global CSRF Protection Missing (Security)
The Flask application (`app.py`) lacks global Cross-Site Request Forgery (CSRF) protection, leaving state-changing endpoints (e.g., `/admin/subscribers`) vulnerable to CSRF attacks.
**Action:** Install `flask-wtf` and enable `CSRFProtect(app)`.

### 5. MonitorService Split-Brain (Reliability)
The `MonitorService` stores state in-memory (`self.nodes`, `self.event_log`), but the production deployment uses `gunicorn` with multiple workers. This causes a "split-brain" state where each worker has its own isolated monitoring state.
**Action:** Use an external state store (e.g., Redis) or a single-process deployment for the monitoring service.

### 6. Hardcoded Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin` / `admin123`) and `app.py` uses a hardcoded `secret_key` ("dev-secret-key").
**Action:** Remove hardcoded credentials and enforce environment variable configuration.

### 7. Split-Brain Task State (Process)
The repository contains both `docs/CURRENT_TASK.md` and `CURRENT_TASK.md`, creating conflicting sources of truth for the active task. This violates the "Single Source of Truth" principle.
**Action:** Consolidate task state into the root `CURRENT_TASK.md` and delete `docs/CURRENT_TASK.md`.

## Medium Severity

### 8. Missing Dependency: python-dotenv (Reliability)
The `scripts/preflight.sh` script relies on `python-dotenv` to load environment variables, but it is missing from `requirements.txt` (though present in `pyproject.toml`). This may cause the preflight check to fail or produce misleading errors.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.
