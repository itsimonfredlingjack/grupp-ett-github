# PR Review Findings

## High Severity

### 1. Missing CSRF Protection on Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks, allowing malicious sites to submit expenses on behalf of authenticated users.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 2. Hardcoded Secret Key in Application Factory
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 3. Missing Test Implementation
The commit message indicates that `tests/monitor/` files were added, but they are missing from the PR changes. This leaves the `MonitorService` and its routes unverified, potentially allowing regressions or bugs to pass unnoticed.
**Action:** Verify that `git add` was run for the test files (e.g., `tests/monitor/test_monitor_service.py`) and ensure they are included in the PR.

### 4. Missing Dependency Updates
`requirements.txt` was not updated to include `flask-socketio`, which is explicitly imported in `app.py`. The application will fail to start in a fresh environment due to `ModuleNotFoundError`.
**Action:** Add `flask-socketio` (and `python-dotenv` if used) to `requirements.txt`.

## Medium Severity

### 5. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`. While both are in-memory, using SQLite ensures the application is ready for SQL-based persistence and validates database constraints as intended.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify if the requirement has changed.

### 6. Brittle Error Handling Logic (Reliability)
In `src/expense_tracker/presentation/routes.py`, error handling relies on string matching of exception messages (e.g., `if "Amount must be greater than 0" in str(e):`). This logic is fragile and will break if the error messages in `ExpenseService` are updated.
**Action:** Define custom exception classes (e.g., `InvalidAmountError`) or use error codes in `src/expense_tracker/business/exceptions.py` to handle errors programmatically.

### 7. Committed Coverage Report
`coverage.xml` is a generated build artifact and should not be committed to the repository. It causes unnecessary repository bloat and potential merge conflicts.
**Action:** Remove `coverage.xml` from the repository and ensure it is listed in `.gitignore`.

## Low Severity

### 8. Inconsistent Route Registration in Tests
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy creates a mismatch between the test environment and production, potentially hiding issues related to relative URLs or path handling.
**Action:** Update the test fixture to register the blueprint at `/expenses` or use the `create_app` factory in tests to mirror the production configuration.
