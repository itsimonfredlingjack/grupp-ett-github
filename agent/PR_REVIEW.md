# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The application lacks Cross-Site Request Forgery (CSRF) protection. The `POST /add` endpoint accepts form submissions without a CSRF token, and `Flask-WTF` is neither installed nor configured. This allows attackers to forge requests on behalf of authenticated users.
**Action:** Install `Flask-WTF`, initialize `CSRFProtect` in `app.py`, and add the CSRF token to all forms.

## High Severity

### 2. Weak Admin Authentication (Security)
The `AdminAuthService` uses a predictable token generation mechanism (`hash(username) % 10000`) and relies on hardcoded credentials (`admin`/`admin123`). This allows trivial unauthorized access to administrative functions.
**Action:** Implement secure password hashing (e.g., `bcrypt`) and use cryptographically secure tokens (e.g., `secrets.token_urlsafe`).

### 3. Hardcoded Secret Key (Security)
The `SECRET_KEY` is hardcoded as `'dev-secret-key'` in `app.py`. If this code is deployed to production, it compromises session security.
**Action:** Load `SECRET_KEY` from environment variables using `os.environ.get()` and ensure the application fails to start if it is missing in production.

### 4. Debug Mode Enabled (Security)
The application entry point in `app.py` runs with `debug=True` by default (`socketio.run(app, debug=True, ...)`). This exposes sensitive debugging information and stack traces in the browser if deployed.
**Action:** Configure debug mode via an environment variable (e.g., `FLASK_DEBUG`) and default to `False`.

## Medium Severity

### 5. Unsafe Float Conversion (Correctness)
The `Expense` model and routes use `float` for monetary values. This leads to precision errors and allows `Infinity` and `NaN` values, which bypass `> 0` validation checks.
**Action:** Use `decimal.Decimal` for all monetary fields and conversions.

### 6. Missing Dependency (Reliability)
`python-dotenv` is added to `pyproject.toml` but is missing from `requirements.txt`. This inconsistency can lead to deployment failures or missing environment variables in production.
**Action:** Add `python-dotenv` to `requirements.txt`.

### 7. Deviation from Persistence Requirement (Correctness)
The `InMemoryExpenseRepository` uses a Python list for storage, deviating from the stated requirement of `sqlite:///:memory:`. This limits the ability to test SQL-specific behavior and constraints.
**Action:** Implement the repository using `sqlite3` with an in-memory database as required.

### 8. CSRF Protection Disabled in Tests (Test Coverage)
The integration tests in `tests/expense_tracker/test_routes.py` explicitly disable CSRF protection (`WTF_CSRF_ENABLED = False`). This masks the absence of CSRF handling in the application code and provides a false sense of security.
**Action:** Enable CSRF in tests and update them to include valid CSRF tokens in requests.
