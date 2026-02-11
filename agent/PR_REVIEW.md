# PR Review Findings

## Critical Severity

### 1. Split-Brain Task State (Process)
The file `docs/CURRENT_TASK.md` exists in the repository, conflicting with the root `CURRENT_TASK.md`. This violates the single-source-of-truth mandate and causes task state divergence (GE-51 vs GE-49).
**Action:** Delete `docs/CURRENT_TASK.md` immediately.

### 2. Stored XSS in Monitor (Security)
The `static/monitor.html` file renders event messages using `innerHTML` without sanitization. An attacker can inject malicious scripts via the `/api/monitor/state` endpoint.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input.

## High Severity

### 3. Missing CSRF Protection (Security)
The application lacks global CSRF protection (e.g., `Flask-WTF`'s `CSRFProtect`). This leaves state-changing endpoints vulnerable to Cross-Site Request Forgery.
**Action:** Initialize `CSRFProtect(app)` in `app.py`.

### 4. Hardcoded Secret Key (Security)
The `app.py` file uses a hardcoded `secret_key` ("dev-secret-key") without checking for an environment variable override. This is insecure for production.
**Action:** Use `os.environ.get("SECRET_KEY", "dev-secret-key")`.

## Medium Severity

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` and WebSocket events are unauthenticated. This allows any network user to inject events or reset dashboard state.
**Action:** Implement authentication for these endpoints.

### 6. Task Status Inconsistency (Process)
`CURRENT_TASK.md` sets the status to `Complete - In Review`, but the feature code (GE-51) appears to be already merged.
**Action:** Update status to `Done` or `Complete` to reflect the merged state.

## Low Severity

### 7. Unsafe Development Defaults (Security)
`app.py` enables `debug=True` and `allow_unsafe_werkzeug=True` in the `__main__` block. Ensure the production entrypoint does not use this block.
**Action:** Verify production command does not run `python app.py`.

### 8. Missing Dependency (Reliability)
`python-dotenv` is missing from `requirements.txt` but is required for local development and scripts like `preflight.sh`.
**Action:** Add `python-dotenv` to `requirements.txt`.
