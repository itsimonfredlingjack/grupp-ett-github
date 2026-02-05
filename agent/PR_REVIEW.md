# PR Review Findings

## High Severity

### 1. Missing CSRF Protection on Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks, allowing malicious sites to submit expenses on behalf of authenticated users.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py` and include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in the form in `index.html`.

### 2. Hardcoded Secret Key in Application Factory
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

## Medium Severity

### 3. Deviation from Data Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` currently uses a Python `list` for storage, whereas the requirements specifically mandated `sqlite:///:memory:`. While both are in-memory, using SQLite ensures the application is ready for SQL-based persistence and validates database constraints as intended.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database or clarify if the requirement has changed.

### 4. Brittle Error Handling Logic (Reliability)
In `src/expense_tracker/presentation/routes.py`, error handling relies on string matching of exception messages (e.g., `if "Amount must be greater than 0" in str(e):`). This logic is fragile and will break if the error messages in `ExpenseService` are updated.
**Action:** Define custom exception classes (e.g., `InvalidAmountError`) or use error codes in `src/expense_tracker/business/exceptions.py` to handle errors programmatically.

## Low Severity

### 5. Inconsistent Route Registration in Tests
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy creates a mismatch between the test environment and production, potentially hiding issues related to relative URLs or path handling.
**Action:** Update the test fixture to register the blueprint at `/expenses` or use the `create_app` factory in tests to mirror the production configuration.
