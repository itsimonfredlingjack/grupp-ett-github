## Critical Severity

### 1. Missing CSRF Protection (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without any CSRF protection. `Flask-WTF` is missing from `requirements.txt` and the form does not include a CSRF token.
**Action:** Add `Flask-WTF` dependency, implement `FlaskForm` with CSRF protection, and include the token in templates.

## High Severity

### 2. Tests Mask Security Vulnerability (Security)
Integration tests in `tests/expense_tracker/test_routes.py` explicitly disable CSRF protection using `app.config["WTF_CSRF_ENABLED"] = False`. This creates a false positive result for security checks.
**Action:** Enable CSRF in tests and update test clients to include valid CSRF tokens or use `Flask-WTF`'s test helpers.

## Medium Severity

### 3. Inappropriate Currency Type (Correctness)
The `Expense` model uses `float` for the `amount` field. Floating-point arithmetic is prone to precision errors and is unsuitable for financial calculations.
**Action:** Change the `amount` field type to `decimal.Decimal` in models and DTOs to ensure precision.

### 4. Unsafe Input Validation (Reliability)
Input validation relies on `float()` conversion which accepts `Infinity` and `NaN` values. While `NaN` fails the `<= 0` check, it can propagate through the system, and `Infinity` bypasses the check entirely.
**Action:** Implement strict validation to ensure the amount is a finite number and a valid decimal.

### 5. Deviation from Persistence Requirements (Architecture)
The `InMemoryExpenseRepository` implementation uses a Python list instead of the required `sqlite:///:memory:` implementation specified in the task description.
**Action:** Update the repository to use an in-memory SQLite database or update the requirements if a list is acceptable for the MVP.

## Low Severity

### 6. Missing Dependency Specification (Configuration)
`Flask-WTF` is required for the recommended CSRF protection fix but is missing from `requirements.txt`.
**Action:** Add `Flask-WTF` to `requirements.txt`.
