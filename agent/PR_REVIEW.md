# PR Review Findings

## Critical Severity

### 1. Missing Authentication on Monitor Endpoints (Security)
The monitoring API endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/state`, `/reset`) are accessible without any authentication. This allows any network user to modify the monitoring state or reset it, compromising the integrity of the monitoring system.
**Action:** Protect these endpoints using the `@require_admin_token` decorator or a similar authentication mechanism.

### 2. Insecure Admin Token Validation (Security)
The `AdminAuthService.validate_session_token` method in `src/sejfa/core/admin_auth.py` validates tokens using `token.startswith("token_")`. This allows any string starting with "token_" to be accepted as a valid session token, completely bypassing authentication.
**Action:** Implement secure token validation, such as checking against a store of active tokens or using cryptographically signed tokens (e.g., JWT).

## High Severity

### 3. Hardcoded Secret Key in Application Factory (Security)
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 4. Thread Safety in MonitorService (Correctness)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` is not thread-safe. The `update_node` method modifies shared state (`self.nodes`, `self.event_log`) without locking. In a concurrent environment like Flask with SocketIO, this can lead to race conditions and data corruption.
**Action:** Use `threading.Lock` to synchronize access to shared state within `MonitorService`.

### 5. Missing CSRF Exemption for Monitor POST Endpoints (Security)
The POST endpoints in `src/sejfa/monitor/monitor_routes.py` are not marked with `@csrf.exempt`. If the application enables global CSRF protection (which is a standard security practice), these endpoints will reject legitimate updates from the monitoring wrapper (which cannot easily provide a CSRF token).
**Action:** Decorate the `update_state`, `reset_monitoring`, and `update_task` endpoints with `@csrf.exempt` (requires importing `csrf` extension).

### 6. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include the CSRF token in the form.

## Medium Severity

### 7. Committed Build Artifact (Reliability)
The file `coverage.xml` has been committed to the repository. This is a generated build artifact and should not be tracked in version control, as it creates noise and merge conflicts.
**Action:** Remove `coverage.xml` from the repository and add it to `.gitignore`.

### 8. Deprecated datetime Usage (Correctness)
The `MonitorService` uses `datetime.utcnow()`, which is deprecated in Python 3.12+. This may cause issues or warnings in future Python versions.
**Action:** Replace `datetime.utcnow()` with `datetime.now(timezone.utc)`.
