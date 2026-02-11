# PR Review Findings

## Critical Severity

### 1. Authentication Bypass in AdminAuthService (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `token_` (e.g. `token_fake`), allowing attackers to bypass authentication and access admin endpoints.
**Action:** Implement proper token validation, preferably using a secure session management library or database lookup.

## High Severity

### 2. Stored XSS in Monitoring Dashboard (Security)
The `static/monitor.html` file renders event messages using `innerHTML` without sanitization. An attacker can inject malicious scripts via the unauthenticated `/api/monitor/state` endpoint, which will be executed in the dashboard viewer's browser.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering.

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated, allowing any network user to inject false events or trigger the XSS vulnerability.
**Action:** Implement authentication for these endpoints.

### 4. Hardcoded Admin Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin`/`admin123`) which are easily guessable and insecure for production.
**Action:** Move credentials to environment variables or a secure database.

### 5. Hardcoded Secret Key (Security)
The `app.py` file sets `app.secret_key = "dev-secret-key"` without checking environment variables, making sessions insecure in production if not overridden.
**Action:** Use `os.environ.get("SECRET_KEY")` to load the secret key from the environment.

### 6. MonitorService Split-Brain (Reliability)
The `MonitorService` stores state in-memory. Since the application is deployed with Gunicorn using multiple workers (as seen in `Dockerfile`), each worker maintains its own isolated state, causing inconsistent dashboard data and "split-brain" behavior.
**Action:** Use a shared data store (e.g., Redis) for monitoring state.

## Medium Severity

### 7. Duplicate Documentation (Process)
`docs/Bygga Agentic Dev Loop-system.md` is a Swedish duplicate of `docs/AGENTIC_DEVOPS_LOOP.md` and should be removed to avoid maintenance issues.
**Action:** Delete `docs/Bygga Agentic Dev Loop-system.md`.

### 8. Missing Dependency: python-dotenv (Reliability)
`python-dotenv` is used in `scripts/preflight.sh` (and likely elsewhere) but is missing from `requirements.txt`.
**Action:** Add `python-dotenv` to `requirements.txt`.

## Verified Changes

### 1. Dependency: flask-socketio
Verified that `flask-socketio>=5.0.0` is present in `requirements.txt`.

### 2. Monitor Hooks
Verified that `.claude/hooks/monitor_client.py` and `.claude/hooks/monitor_hook.py` exist and are not deleted.
