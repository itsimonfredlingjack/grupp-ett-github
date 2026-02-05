# PR Review Findings

## High Severity

### 1. Stored XSS Vulnerability in Dashboard (Security)
The dashboard `static/monitor.html` renders event messages using `innerHTML` without sanitization: `<div>${event.message || 'Active'}</div>`. A malicious task title or tool output containing JavaScript could execute arbitrary code in the viewer's browser.
**Action:** Use `textContent` or a sanitization library to render user-controlled content safely.

### 2. Missing Authentication on Monitor Endpoints (Security)
The monitoring API endpoints (e.g., `/api/monitor/state`) are publicly accessible without any authentication. This allows unprivileged users to inject fake events or reset the monitoring state.
**Action:** Implement authentication checks (e.g., API key or session token) for state modification endpoints.

### 3. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form.

### 4. Hardcoded Secret Key (Security)
The application uses a hardcoded `SECRET_KEY` ("dev-secret-key") in `app.py`. This compromises session security.
**Action:** Load `SECRET_KEY` from environment variables and ensure it is not hardcoded in production.

### 5. Missing Automated Tests for Monitoring (Test Coverage)
The monitoring system (`src/sejfa/monitor/`) lacks automated unit or integration tests in the `tests/` directory. `QUICK_TEST.sh` is insufficient for CI/CD verification.
**Action:** Add `tests/monitor/test_monitor_routes.py` and `tests/monitor/test_monitor_service.py` with comprehensive coverage.

## Medium Severity

### 6. Thread Safety Issues in MonitorService (Reliability)
`MonitorService.update_node` modifies shared state (`self.nodes`, `self.event_log`) without locking. In a threaded Flask environment, this can lead to race conditions and data corruption.
**Action:** Use `threading.Lock()` to synchronize access to shared resources.

### 7. Global State Dependency (Maintainability)
`src/sejfa/monitor/monitor_routes.py` relies on module-level global variables (`monitor_service`, `socketio`) injected via `create_monitor_blueprint`. This creates tight coupling and makes testing difficult.
**Action:** Use Flask's `current_app` context or closure-based blueprint factories to manage dependencies.

### 8. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database.
