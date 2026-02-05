# PR Review Findings

## High Severity

### 1. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 2. Hardcoded Secret Key in Application Factory (Security)
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 3. Monitor API Routes Missing CSRF Exemption (Security)
The `POST` endpoints in `src/sejfa/monitor/monitor_routes.py` (`/state`, `/reset`) are not exempted from CSRF protection. If `CSRFProtect` is enabled globally (as required), these endpoints will reject requests from the `claude-monitor-wrapper.sh` script, breaking the monitoring loop.
**Action:** Apply `@csrf.exempt` to the monitor blueprint or individual routes to allow external tool access.

## Medium Severity

### 4. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`. Using SQLite ensures the application is ready for SQL-based persistence and validates database constraints.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify if the requirement has changed.

### 5. Brittle Error Handling Logic (Reliability)
In `src/expense_tracker/presentation/routes.py`, error handling relies on string matching of exception messages (e.g., `if "Amount must be greater than 0" in str(e):`). This logic is fragile and will break if the error messages in `ExpenseService` are updated.
**Action:** Define custom exception classes (e.g., `InvalidAmountError`) or use error codes in `src/expense_tracker/business/exceptions.py` to handle errors programmatically.

### 6. Global State Usage in Monitor Blueprint Factory (Reliability)
`create_monitor_blueprint` in `src/sejfa/monitor/monitor_routes.py` relies on `global` variables (`monitor_service`, `socketio`) to inject dependencies. This prevents creating multiple independent application instances and makes the code harder to maintain.
**Action:** Refactor routes to be defined within the `create_monitor_blueprint` scope (closure) to capture dependencies directly.

## Low Severity

### 7. Manual App Construction in Monitor Tests (Reliability)
`tests/monitor/test_monitor_routes.py` manually constructs the `Flask` application instead of using the `create_app` factory. This creates a risk where the test environment diverges from production configuration.
**Action:** Update test fixtures to use `app.create_app()` to ensure the tested application matches the production configuration.

### 8. Inconsistent Route Registration in Tests (Reliability)
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy creates a mismatch between the test environment and production.
**Action:** Update the test fixture to register the blueprint at `/expenses` or use the `create_app` factory in tests.
