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

### 5. Missing Dependency: python-dotenv (Reliability)
The `scripts/preflight.sh` script relies on `python-dotenv` to load environment variables from `.env`, but it is missing from `requirements.txt`. This causes the script to fail in environments where the package is not pre-installed.
**Action:** Add `python-dotenv` to `requirements.txt`.

## Medium Severity

### 6. Missing Global CSRF Protection (Security)
The application (`app.py`) does not enable Cross-Site Request Forgery (CSRF) protection. State-changing endpoints are vulnerable to CSRF attacks.
**Action:** Install `flask-wtf` and initialize `CSRFProtect(app)` in `app.py`.

### 7. Hardcoded Flask Secret Key (Security)
The `app.py` file sets `app.secret_key` to a hardcoded string (`"dev-secret-key"`). This compromises session security if deployed.
**Action:** Load `SECRET_KEY` from environment variables.

## Low Severity

### 8. Unused Helper Method in Tests (Maintainability)
The `tests/newsflash/test_color_scheme.py` file contains a method `extract_hex_color` in the `TestAccessibilityContrast` class which is never called. Unused code creates noise and should be removed.
**Action:** Delete the unused helper method `extract_hex_color`.
