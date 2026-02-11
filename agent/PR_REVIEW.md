# PR Review Findings

## Critical Severity

### 1. Admin Authentication Bypass (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains a logic flaw in `validate_session_token`. It accepts any token string starting with `token_`, allowing attackers to bypass authentication completely by crafting a fake token (e.g., `Authorization: Bearer token_fake`).
**Action:** Implement proper token validation (e.g., check against a stored session or use signed JWTs).

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin` / `admin123`) in the source code. This is a severe security risk as these credentials are exposed in the repository.
**Action:** Remove hardcoded credentials and use environment variables or a database for admin authentication.

### 3. Split-Brain Task State (Process)
The file `docs/CURRENT_TASK.md` exists in the repository, conflicting with the root `CURRENT_TASK.md`. This violates the single-source-of-truth mandate and causes task state divergence (GE-51 vs GE-49).
**Action:** Delete `docs/CURRENT_TASK.md` immediately.

### 4. Stored XSS in Monitor (Security)
The `static/monitor.html` file renders event messages using `innerHTML` without sanitization. An attacker can inject malicious scripts via the `/api/monitor/state` endpoint.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input.

## High Severity

### 5. Missing CSRF Protection (Security)
The application lacks global CSRF protection (e.g., `Flask-WTF`'s `CSRFProtect`). This leaves state-changing endpoints vulnerable to Cross-Site Request Forgery.
**Action:** Initialize `CSRFProtect(app)` in `app.py`.

### 6. Hardcoded Secret Key (Security)
The `app.py` file uses a hardcoded `secret_key` ("dev-secret-key") without checking for an environment variable override. This is insecure for production.
**Action:** Use `os.environ.get("SECRET_KEY", "dev-secret-key")`.

## Medium Severity

### 7. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` and WebSocket events are unauthenticated. This allows any network user to inject events or reset dashboard state.
**Action:** Implement authentication for these endpoints.

## Low Severity

### 8. Unsafe Development Defaults (Security)
`app.py` enables `debug=True` and `allow_unsafe_werkzeug=True` in the `__main__` block. Ensure the production entrypoint does not use this block.
**Action:** Verify production command does not run `python app.py`.
