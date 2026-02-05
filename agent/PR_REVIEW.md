# PR Review Findings

## High Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`admin`/`admin123`). This allows unauthorized access to administrative functions in any deployed environment.
**Action:** Replace hardcoded credentials with environment variables or a secure database storage mechanism.

### 2. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` dashboard uses `innerHTML` to render event messages (`${event.message}`) without sanitization. This allows Stored Cross-Site Scripting (XSS) if a malicious payload is injected into the monitoring log.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering in the dashboard.

### 3. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form.

### 4. Hardcoded Secret Key in Application Factory (Security)
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables and ensure the application fails to start if it is missing in production.

### 5. Monitor API Routes Missing CSRF Exemption (Security)
The `POST` endpoints in `src/sejfa/monitor/monitor_routes.py` (`/state`, `/reset`) are not exempted from CSRF protection. Enabling global CSRF protection will break the `claude-monitor-wrapper.sh` script integration.
**Action:** Apply `@csrf.exempt` to the monitor blueprint or individual API routes to allow external tool access.

## Medium Severity

### 6. Permissive CORS on SocketIO (Security)
The `SocketIO` instance in `app.py` is configured with `cors_allowed_origins="*"`. This allows any website to connect to the WebSocket server, potentially enabling Cross-Site WebSocket Hijacking (CSWSH).
**Action:** Restrict `cors_allowed_origins` to trusted domains or configured environment variables.

### 7. Global State Usage in Monitor Blueprint Factory (Reliability)
`create_monitor_blueprint` in `src/sejfa/monitor/monitor_routes.py` relies on `global` variables (`monitor_service`, `socketio`) to inject dependencies. This prevents creating multiple independent application instances and hampers testing.
**Action:** Refactor routes to be defined within the `create_monitor_blueprint` scope (closure) to capture dependencies directly.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`. Using SQLite ensures the application is ready for SQL-based persistence and validates database constraints.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database.
