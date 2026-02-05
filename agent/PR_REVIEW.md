# Automated PR Review Findings

## High Severity

### 1. Stored XSS Vulnerability in Dashboard (Security)
The dashboard `static/monitor.html` renders event messages using `innerHTML` without sanitization: `<div>${event.message || 'Active'}</div>`. A malicious task title or tool output containing JavaScript could execute arbitrary code in the viewer's browser.
**Action:** Use `textContent` or a sanitization library (e.g., DOMPurify) to render user-controlled content safely.

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (username "admin", password "[REDACTED]"). This is a critical security vulnerability that allows trivial unauthorized access.
**Action:** Store credentials in a secure database or use environment variables/secrets management for the initial admin account.

### 3. Missing Authentication on Monitor Endpoints (Security)
The monitoring API endpoints (e.g., `/api/monitor/state`, `/api/monitor/reset`) in `src/sejfa/monitor/monitor_routes.py` are publicly accessible without any authentication. This allows unprivileged users to inject fake events, modify task info, or reset the monitoring state.
**Action:** Implement authentication checks (e.g., `@require_admin_token`) for all state modification endpoints.

### 4. Hardcoded Secret Key (Security)
The application uses a hardcoded `SECRET_KEY` ("dev-secret-key") in `app.py`. This compromises session security and allows attackers to forge session cookies.
**Action:** Load `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 5. Missing CSRF Protection (Security)
The application lacks global CSRF protection in `app.py`, and the `ExpenseTracker` form in `src/expense_tracker/presentation/routes.py` accepts POST requests without token verification. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Initialize `Flask-WTF`'s `CSRFProtect(app)` in `app.py` and include hidden CSRF token fields in all forms.

## Medium Severity

### 6. Thread Safety Issues in MonitorService (Reliability)
`MonitorService.update_node` and other methods in `src/sejfa/monitor/monitor_service.py` modify shared state (`self.nodes`, `self.event_log`) without locking. In a threaded Flask environment (e.g., with Gunicorn or SocketIO), this can lead to race conditions and data corruption.
**Action:** Use `threading.Lock` to synchronize access to shared resources within `MonitorService`.

### 7. Data Persistence Requirement Violation (Correctness)
The `InMemoryExpenseRepository` in `src/expense_tracker/data/repository.py` uses a Python `list` for storage, whereas the requirements mandated `sqlite:///:memory:`. This prevents validation of SQL constraints and proper database integration testing.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database to match production-like behavior.

### 8. Missing Automated Tests for Monitoring (Test Coverage)
The monitoring system (`src/sejfa/monitor/`) lacks automated unit or integration tests in the `tests/` directory. The current `QUICK_TEST.sh` script is insufficient for CI/CD verification.
**Action:** Add `tests/monitor/test_monitor_routes.py` and `tests/monitor/test_monitor_service.py` with comprehensive test coverage.
