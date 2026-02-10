# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "admin123"`). This allows anyone with access to the source code to gain full administrative access.
**Action:** Remove hardcoded credentials. Use environment variables or a secure database for credential storage.

### 2. Insecure Token Validation (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` validates tokens by checking `startswith("token_")`. This allows an attacker to bypass authentication by providing any string starting with `token_`.
**Action:** Implement secure token validation (e.g., check against a stored valid token list or use signed JWTs).

## High Severity

### 3. CI Branch Workflow Missing Dependencies (Reliability)
The `.github/workflows/ci_branch.yml` workflow manually installs dependencies (`pip install pytest pytest-cov ruff flask`) but fails to include `flask-socketio`, which is required by `app.py`. This will likely cause test collection failures in CI.
**Action:** Update the workflow to install dependencies from `requirements.txt` (`pip install -r requirements.txt`) or explicitly add `flask-socketio`.

### 4. Security Job Missing Dependencies (Reliability)
The `security` job in `.github/workflows/ci_branch.yml` also manually installs `flask pytest` but misses `flask-socketio`, potentially leading to incomplete checks or runtime errors during analysis.
**Action:** Update the job to install dependencies from `requirements.txt`.

### 5. Missing CSRF Protection (Security)
Global CSRF protection is not enabled in `app.py` (no `CSRFProtect`), and `Flask-WTF` is missing from `requirements.txt`. This leaves the application vulnerable to Cross-Site Request Forgery attacks.
**Action:** Install `Flask-WTF`, add it to `requirements.txt`, and initialize `CSRFProtect` in `app.py`.

## Medium Severity

### 6. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/state`, `/reset`) are unauthenticated, allowing any network user to modify the monitoring state.
**Action:** Implement authentication (e.g., API key or AdminAuthService) for these endpoints.

### 7. Unsafe Application Configuration (Security)
The `app.py` file enables `debug=True` and `allow_unsafe_werkzeug=True` in the main execution block. This is unsafe for production deployments.
**Action:** Use environment variables (e.g., `FLASK_DEBUG`) to control these settings.

## Low Severity

### 8. Hardcoded Monitoring URL (Maintainability)
The `monitor_client.py` script uses a hardcoded `http://localhost:5000` URL, which may cause connection issues in containerized environments or production.
**Action:** Use an environment variable (e.g., `MONITOR_URL`) with a default, to allow configuration.
