# PR Review Findings

## Critical Severity

### 1. Admin Auth Bypass (Security)
The `AdminAuthService.validate_session_token` method insecurely validates tokens using `startswith("token_")`. This allows any user to bypass authentication by providing a fake token like `token_fake`.
**Action:** Implement secure token validation using exact matching or a cryptographic signature verification (e.g., JWT).

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` contains hardcoded credentials (`admin`/`admin123`) and uses a weak token generation algorithm (`hash(username) % 10000`). This makes the admin interface easily compromisable and vulnerable to brute force or prediction attacks.
**Action:** Remove hardcoded credentials, use a database for user storage with hashed passwords, and implement secure session management.

### 3. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` dashboard renders `event.message` using `innerHTML` without sanitization. An attacker can inject malicious scripts via the unauthenticated `/api/monitor/state` endpoint, leading to Stored Cross-Site Scripting (XSS).
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify before rendering.

## High Severity

### 4. Unauthenticated Monitor Endpoints (Security)
The `/api/monitor/state`, `/api/monitor/reset`, and `/api/monitor/task` endpoints in `src/sejfa/monitor/monitor_routes.py` lack authentication checks. This allows unauthorized users to manipulate the monitoring dashboard and inject false data.
**Action:** Protect these endpoints by requiring the Admin Session Token or a dedicated API key.

### 5. Hardcoded Secret Key in Application Factory (Security)
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 6. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

## Medium Severity

### 7. Missing Production Dependency (Correctness)
The `app.py` file imports `flask_socketio`, but this dependency is missing from `requirements.txt`. This will cause the application to crash in production environments where dependencies are installed from this file.
**Action:** Add `flask-socketio>=5.0.0` to `requirements.txt`.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. Using SQLite ensures the application is ready for SQL-based persistence.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database.
