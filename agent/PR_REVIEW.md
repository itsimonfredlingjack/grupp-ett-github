# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Add Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token, and the `index.html` template lacks the hidden token field. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py`, use `FlaskForm`, or manually verify CSRF tokens in `routes.py` and templates.

## High Severity

### 2. Hardcoded Secret Key in Application Factory
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 3. Inappropriate Data Type for Currency (Correctness)
The `Expense` model uses `float` for the `amount` field. Floating-point arithmetic is prone to precision errors (e.g., `0.1 + 0.2 != 0.3`) and is unsuitable for financial data.
**Action:** Use `decimal.Decimal` or store amounts as integer cents to ensure precision.

### 4. Invalid Input Acceptance (Infinity/NaN)
The `ExpenseService` relies on Python's `float()` casting which accepts `Infinity` and `NaN`. Since `float('inf') > 0` is true, these values bypass validation and can corrupt data integrity (e.g., infinite totals).
**Action:** Update `_validate_amount` in `src/expense_tracker/business/service.py` to explicitly reject `math.isinf(amount)` and `math.isnan(amount)`.

## Medium Severity

### 5. Deviation from SQLite Requirement (Correctness)
The `InMemoryExpenseRepository` implementation uses a Python `list` for storage, whereas requirements explicitly mandate `sqlite:///:memory:`. This architectural deviation affects data integrity constraints and query capabilities.
**Action:** Refactor `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database as required.

### 6. Integration Tests Mask Security Risks
The integration tests in `tests/expense_tracker/test_routes.py` explicitly disable CSRF protection via `app.config["WTF_CSRF_ENABLED"] = False`. This configuration hides the absence of CSRF handling in the actual application code.
**Action:** Enable `WTF_CSRF_ENABLED` in tests and update test clients to inject valid CSRF tokens during `POST` requests.

## Low Severity

### 7. Inconsistent Route Registration in Tests
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy creates a mismatch between the test environment and production, potentially hiding issues related to relative URLs.
**Action:** Update the test setup to register the blueprint at `/expenses` to match `app.py`.

### 8. Brittle Error Handling Logic in Tests (Reliability)
Tests in `tests/expense_tracker/test_routes.py` rely on partial string matching of Swedish error messages (e.g., "större än 0"). This approach is fragile and will break if UI text changes.
**Action:** Use error codes or named constants for validation messages to verify errors programmatically.
