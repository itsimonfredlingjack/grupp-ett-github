# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Add Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token, and the `index.html` template lacks the hidden token field. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Configure `Flask-WTF`'s `CSRFProtect` in `app.py`, use `FlaskForm`, or manually verify CSRF tokens in `routes.py` and templates.

## High Severity

### 2. Invalid Input Acceptance (Infinity/NaN)
The `ExpenseService` relies on Python's `float()` casting which accepts `Infinity` and `NaN`. Since `float('inf') > 0` is true and `float('nan') <= 0` is false, these values bypass validation and can corrupt data integrity (e.g., infinite totals).
**Action:** Update `_validate_amount` in `src/expense_tracker/business/service.py` to explicitly reject `math.isinf(amount)` and `math.isnan(amount)`.

## Medium Severity

### 3. Deviation from SQLite Requirement (Correctness)
The `InMemoryExpenseRepository` implementation uses a Python `list` for storage, whereas `CURRENT_TASK.md` and the requirements explicitly mandate `sqlite:///:memory:`. This architectural deviation affects data integrity constraints and query capabilities.
**Action:** Refactor `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database as required, or officially update the requirements to permit list-based storage.

### 4. Integration Tests Mask Security Risks
The integration tests in `tests/expense_tracker/test_routes.py` explicitly disable CSRF protection via `app.config["WTF_CSRF_ENABLED"] = False`. This configuration hides the absence of CSRF handling in the actual application code, leading to false confidence in security.
**Action:** Enable `WTF_CSRF_ENABLED` in tests and update test clients to inject valid CSRF tokens during `POST` requests.

## Low Severity

### 5. Inconsistent Route Registration in Tests
The test fixture in `tests/expense_tracker/test_routes.py` registers the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy means tests are not verifying the actual URL structure used in production.
**Action:** Update the test fixture to register the blueprint at `/expenses` to match `app.py` configuration.
