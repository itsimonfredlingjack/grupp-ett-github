# PR Review Findings

## High Severity

### 1. Missing CSRF Protection on Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks, allowing malicious sites to submit expenses on behalf of authenticated users.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 2. Hardcoded Secret Key in Application Factory
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 3. Weak Assertions Masking Failures (Reliability)
Tests in `tests/monitor/test_monitor_routes.py` use assertions like `assert response.status_code in [200, 500]`. This allows server errors (500) to pass as success, effectively disabling the test's ability to catch regressions or bugs.
**Action:** Update tests to assert only the expected success code (e.g., `assert response.status_code == 200`) and verify the response body content.

### 4. Thread Safety in MonitorService (Concurrency)
The `MonitorService.update_node` method modifies shared state (`self.nodes`, `self.current_node`) without locking. In a threaded Flask/SocketIO environment, concurrent updates can lead to race conditions and inconsistent state.
**Action:** Use `threading.Lock()` to protect critical sections in `update_node` and `reset`.

### 5. Missing CSRF Protection on Monitor Routes (Security)
The `POST` endpoints in `src/sejfa/monitor/monitor_routes.py` lack CSRF protection or explicit exemption. If global CSRF protection is enabled, these endpoints will fail for external clients (like the bash wrapper) unless exempted.
**Action:** Apply `@csrf.exempt` to the monitor API routes if they are intended for external use, or require an API key/token.

## Medium Severity

### 6. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`. While both are in-memory, using SQLite ensures the application is ready for SQL-based persistence and validates database constraints as intended.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify if the requirement has changed.

### 7. Brittle Error Handling Logic (Reliability)
In `src/expense_tracker/presentation/routes.py`, error handling relies on string matching of exception messages (e.g., `if "Amount must be greater than 0" in str(e):`). This logic is fragile and will break if the error messages in `ExpenseService` are updated.
**Action:** Define custom exception classes (e.g., `InvalidAmountError`) or use error codes in `src/expense_tracker/business/exceptions.py` to handle errors programmatically.

## Low Severity

### 8. Testing Non-Existent Endpoints (Correctness)
Tests in `tests/monitor/test_monitor_routes.py` verify endpoints like `/api/monitor/health` and `/metrics` which do not exist in `monitor_routes.py`. Asserting `status_code in [200, 404]` for these ensures they always pass but provides no value.
**Action:** Remove tests for non-existent endpoints or implement the endpoints.
