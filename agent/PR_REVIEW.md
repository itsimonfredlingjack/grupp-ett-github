# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The `Flask-WTF` dependency was added to `requirements.txt`, but `CSRFProtect` is not initialized in `app.py`. The `POST /add` endpoint and others remain vulnerable to Cross-Site Request Forgery.
**Action:** Initialize `CSRFProtect(app)` in `create_app` and add CSRF tokens to forms.

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` relies on hardcoded credentials (`admin`/`admin123`) and a predictable token generation mechanism. This allows unauthorized access to administrative functions.
**Action:** Implement secure password hashing (e.g., `bcrypt`) and use cryptographically secure tokens.

## High Severity

### 3. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. This compromises session security if deployed to production.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and fail if missing in production.

### 4. Debug Mode Enabled (Security)
The application runs with `debug=True` by default in `app.py`. This exposes sensitive debugging information and stack traces in the browser.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

## Medium Severity

### 5. Lowered Test Coverage (Reliability)
The CI coverage threshold was lowered from 80% to 70% in `.github/workflows/ci.yml`. This masks potential regressions and reduces code quality standards.
**Action:** Restore the 80% threshold and add tests to cover the new code or exclude specific files.

### 6. Deprecated Date Usage (Correctness)
`MonitorService` in `src/sejfa/monitor/monitor_service.py` uses `datetime.utcnow()`, which is deprecated in Python 3.12. This may cause issues in future Python versions.
**Action:** Replace with `datetime.now(datetime.timezone.utc)`.

### 7. Unsafe Werkzeug Configuration (Reliability)
`app.py` enables `allow_unsafe_werkzeug=True`. This suggests the development server is intended for use in environments where it shouldn't be, or masks configuration issues.
**Action:** Use a production-ready WSGI server like `gunicorn` for deployment instead of the Flask development server.
