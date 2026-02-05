# PR Review: 137

**Review Summary:**
The ExpenseTracker MVP implementation is functional but has critical security and compliance issues. The storage implementation deviates from requirements, and the application lacks CSRF protection.

## Critical Severity

### 1. Missing CSRF Protection (Security)
The `POST /add` route in `src/expense_tracker/presentation/routes.py` and the form in `templates/expense_tracker/index.html` lack CSRF protection. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Action:** Enable CSRF protection (e.g., using Flask-WTF) and include the CSRF token in the form.

## High Severity

### 2. Insecure Storage Implementation (Compliance)
The `InMemoryExpenseRepository` uses a Python list (`self._expenses = []`) instead of the required `sqlite:///:memory:` implementation. This deviates from the technical requirements specified in `CURRENT_TASK.md` and poses a risk of data loss or inconsistency patterns not matching production DBs.
**Action:** Refactor `InMemoryExpenseRepository` to use SQLite in-memory database.

## Medium Severity

### 3. Debug Mode Enabled in Main (Security)
`app.py` enables debug mode (`app.run(debug=True)`) in the `__main__` block. While convenient for development, this poses a security risk if the application is executed directly in a production environment.
**Action:** Remove `debug=True` or wrap it in an environment check (e.g., `os.getenv("FLASK_DEBUG")`).

### 4. Route Configuration Mismatch (Reliability)
Integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at `/`, whereas `app.py` registers it at `/expenses`. This discrepancy means tests do not verify the actual URL structure used in the application.
**Action:** Update tests to register the blueprint at `/expenses` to match `app.py`.

### 5. Hardcoded Secret Key (Security)
`app.py` sets `app.secret_key = "dev-secret-key"`. Hardcoding secrets is a bad practice and poses a security risk if leaked to production.
**Action:** Configure the secret key to be loaded from an environment variable.

### 6. Missing Test for Non-Numeric Input (Reliability)
There is no explicit test case in `tests/expense_tracker/test_routes.py` verifying that non-numeric input for 'amount' is handled correctly.
**Action:** Add a test case submitting a non-numeric string (e.g., "abc") to ensure the error handling works as expected.

## Low Severity

### 7. Input Validation for Infinite Values (Reliability)
The input validation allows infinite values (e.g., `float("inf")`) for the amount. This can break calculations like `get_total_amount`.
**Action:** Add validation to reject infinite or NaN values in `ExpenseService`.
