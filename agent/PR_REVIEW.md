# Automated PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username: "admin"`, `password: "***"`). This allows anyone with access to the source code to gain full administrative access.
**Action:** Remove hardcoded credentials. Use environment variables or a secure database for credential storage.

### 2. Subscription Data Loss (Correctness)
The `SubscriptionService` in `src/sejfa/newsflash/business/subscription_service.py` validates and normalizes subscription data but does not persist it (no database or file storage). The `subscribe_confirm` route flashes a success message, misleading users into thinking they are subscribed.
**Action:** Implement a `SubscriptionRepository` to persist subscriber data to a database (e.g., SQLite/SQLAlchemy).

## High Severity

### 3. Insecure Token Validation (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` validates tokens by checking `startswith("token_")`. This allows an attacker to bypass authentication by providing any string starting with `token_`.
**Action:** Implement secure token validation (e.g., check against a stored valid token list or use signed JWTs).

### 4. Monitor API Incompatibility (Correctness)
The `monitor_client.py` sends `action` ("start"/"complete") and `task_id`, but `monitor_routes.py` expects `status` ("running"/"completed"). Consequently, task status updates are ignored by the server, and the dashboard never updates task state.
**Action:** Update `monitor_client.py` to send `status` matching the server's expectation, or update `monitor_routes.py` to handle `action`.

### 5. Hardcoded Secret Key (Security)
The application uses a hardcoded `SECRET_KEY` ("dev-secret-key") in `app.py` without attempting to load from environment variables.
**Action:** Load `SECRET_KEY` from an environment variable (e.g., `os.getenv("SECRET_KEY")`) and fail or warn if not set in production.

### 6. Missing CSRF Protection (Security)
Global CSRF protection is not enabled in `app.py` (no `CSRFProtect`), and `Flask-WTF` is missing from `requirements.txt`. The subscription form is vulnerable to Cross-Site Request Forgery.
**Action:** Install `Flask-WTF`, add to `requirements.txt`, and initialize `CSRFProtect(app)` in `app.py`.

## Medium Severity

### 7. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/state`, `/reset`) are unauthenticated, allowing any network user to modify the monitoring state.
**Action:** Implement authentication for these endpoints (e.g., using `AdminAuthService` or a dedicated API key).

### 8. Missing Dependencies (Reliability)
`flask-socketio`, `Flask-WTF`, and `python-dotenv` are missing from `requirements.txt` and/or CI workflows (`ci_branch.yml`), despite being required by the application (`app.py` imports `flask_socketio`, `pyproject.toml` lists `python-dotenv`). This causes CI failures and runtime errors in fresh environments.
**Action:** Add specific dependencies to `requirements.txt` and update CI to install from it.
