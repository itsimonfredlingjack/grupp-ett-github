# PR Review Findings

## Critical Severity

### 1. Missing Test Files (Correctness)
Tests for `MonitorService` and `MonitorRoutes` were claimed to be added in commit `6c14fc5` but are missing from the codebase (`tests/monitor/` does not exist). This leaves new functionality unverified and violates the commit message claim.
**Action:** Restore the missing test files or revert the changes if the tests are not ready.

### 2. Hardcoded Admin Credentials (Security)
The file `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`"username": "admin", "password": "admin123"`). This is a critical security vulnerability that allows trivial unauthorized access.
**Action:** Remove hardcoded credentials. Use environment variables or a secure secret management solution.

## High Severity

### 3. Authentication Bypass (Security)
Monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`, `/reset`) are unprotected. Anyone with network access can manipulate the monitoring state or reset it.
**Action:** Implement authentication (e.g., `@login_required` or API key validation) for all sensitive monitoring endpoints.

### 4. Stored XSS Vulnerability (Security)
The file `static/monitor.html` uses `innerHTML` to render event messages without sanitization. This allows an attacker to inject malicious scripts via the `message` field of a monitoring event.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

## Medium Severity

### 5. Regression: Missing Error Handling (Reliability)
The commit message for `6c14fc5` claims to fix 500 errors by using `request.get_json(silent=True)`, but the code in `src/sejfa/monitor/monitor_routes.py` still uses `request.get_json()` without `silent=True`. This will raise a 400 Bad Request (or 500 depending on handler) if the request body is missing or invalid.
**Action:** Update `monitor_routes.py` to use `request.get_json(silent=True)` and handle `None` result.

### 6. Unsafe Debug Configuration (Security)
The `app.py` file enables `debug=True` and `allow_unsafe_werkzeug=True`. This is dangerous for production deployments as it exposes the interactive debugger and allows arbitrary code execution if an error occurs.
**Action:** Ensure `debug=False` in production contexts, preferably controlled by an environment variable.

## Low Severity

### 7. Generated File Committed (Maintainability)
The file `coverage.xml` (709 lines) is committed to the repository. Generated artifacts should not be tracked in version control as they bloat the history and cause merge conflicts.
**Action:** Add `coverage.xml` to `.gitignore` and remove it from the repository.

### 8. Deprecated Method Usage (Maintainability)
The method `datetime.utcnow()` is used in `src/sejfa/monitor/monitor_routes.py`. This method is deprecated in Python 3.12 and should be replaced with timezone-aware alternatives.
**Action:** Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.
