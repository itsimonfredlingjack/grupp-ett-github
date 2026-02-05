# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Add Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token, and the `index.html` template lacks the hidden token field. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py`, use `FlaskForm`, or manually verify CSRF tokens in `routes.py` and templates.

## High Severity

### 2. Hardcoded Secret Key in Application Factory
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. This insecure configuration compromises session security and cryptographic signatures in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 3. Invalid Input Acceptance (Infinity/NaN)
The `ExpenseService` relies on Python's `float()` casting which accepts `Infinity` and `NaN`. Since `float('inf') > 0` is true, these values bypass validation and can corrupt data integrity (e.g., infinite totals).
**Action:** Update `_validate_amount` in `src/expense_tracker/business/service.py` to explicitly reject `math.isinf(amount)` and `math.isnan(amount)`.

## Medium Severity

### 4. Deviation from SQLite Requirement (Correctness)
The `InMemoryExpenseRepository` implementation uses a Python `list` for storage, whereas requirements explicitly mandate `sqlite:///:memory:`. This architectural deviation affects data integrity constraints and query capabilities.
**Action:** Refactor `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database as required.

### 5. Integration Tests Mask Security Risks
The integration tests in `tests/expense_tracker/test_routes.py` explicitly disable CSRF protection via `app.config["WTF_CSRF_ENABLED"] = False`. This configuration hides the absence of CSRF handling in the actual application code.
**Action:** Enable `WTF_CSRF_ENABLED` in tests and update test clients to inject valid CSRF tokens during `POST` requests.

## Low Severity

### 6. Inconsistent Route Registration in Tests
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy creates a risk where path-dependent logic (e.g., relative redirects) works in tests but fails in production.
**Action:** Update tests to register the blueprint at `/expenses` or use `url_for` consistently to ensure path independence.
