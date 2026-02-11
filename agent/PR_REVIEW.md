# Automated PR Review Findings

## Critical Severity

### 1. Authentication Bypass in AdminAuthService (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` accepts any token starting with `token_` (e.g., `token_fake`), allowing unauthorized access to admin endpoints.
**Action:** Implement proper token validation (e.g., check against a stored list of active sessions or use signed JWTs).

### 2. Stored Cross-Site Scripting (XSS) in Monitor Dashboard (Security)
The `static/monitor.html` file renders event messages using `innerHTML` without sanitization. An attacker can inject malicious scripts via the `/api/monitor/state` endpoint which will execute in the browser of anyone viewing the dashboard.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

## High Severity

### 3. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` uses hardcoded credentials (`admin`/`admin123`). This is insecure for any deployment.
**Action:** Use environment variables or a database for credential storage and hashing.

### 4. Split-Brain Monitoring State (Reliability)
The `MonitorService` stores state in-memory, but the `Dockerfile` configures `gunicorn` with 4 workers. This causes a "split-brain" issue where monitoring updates are isolated to a single worker process and not shared.
**Action:** Use an external store (e.g., Redis) or configure gunicorn to use a single worker (`--workers 1`).

### 5. Missing Global CSRF Protection (Security)
The application (`app.py`) does not enable Cross-Site Request Forgery (CSRF) protection. State-changing endpoints are vulnerable to CSRF attacks.
**Action:** Install `flask-wtf` and initialize `CSRFProtect(app)` in `app.py`.

### 6. Duplicate Task Memory (Correctness)
The repository contains two conflicting task memory files: the root `CURRENT_TASK.md` and `docs/CURRENT_TASK.md`. This violates the single source of truth principle and can lead to divergent task states.
**Action:** Unify the task state in the root `CURRENT_TASK.md` and delete `docs/CURRENT_TASK.md`.

## Medium Severity

### 7. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`) are unauthenticated, allowing any network user to inject false events or reset the dashboard.
**Action:** Implement authentication (e.g., API key or shared secret) for these endpoints.

### 8. Hardcoded Secret Key (Security)
The `app.py` file sets `app.secret_key = "dev-secret-key"` without an environment variable override mechanism, making session cookies vulnerable if the code is public.
**Action:** Update `app.py` to use `os.environ.get("SECRET_KEY", "dev-secret-key")`.
