# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks, allowing malicious sites to submit expenses on behalf of authenticated users.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 2. Insecure Application Configuration (Security)
The application configuration in `app.py` uses a hardcoded secret key (`"dev-secret-key"`), enables `debug=True`, and allows `unsafe_werkzeug` in the main execution block. This compromises session security and exposes debug information in production.
**Action:** Load `SECRET_KEY` from environment variables, and ensure `debug` and `allow_unsafe_werkzeug` are disabled in production environments.

## High Severity

### 3. Missing Dependency: flask-socketio (Reliability)
The application code (`app.py`, `monitor_routes.py`) imports `flask_socketio`, but it is missing from `requirements.txt`. This causes runtime errors and CI failures.
**Action:** Add `flask-socketio>=5.0.0` to `requirements.txt`.

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows unauthorized users to modify the monitor state or inject false events.
**Action:** Implement authentication for these endpoints, such as checking for an admin session or API key.

## Medium Severity

### 5. Inaccurate PR Review Findings (Correctness)
The previous `agent/PR_REVIEW.md` content incorrectly claimed that `.claude/hooks/monitor_client.py` and `monitor_hook.py` were deleted, whereas they exist in the codebase. It also removed the valid finding regarding missing CSRF protection.
**Action:** This file has been updated to reflect the actual state of the codebase.

### 6. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` in `src/expense_tracker/data/repository.py` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. This limits the ability to test SQL interactions and constraints.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify the requirement change.
