# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Expense Form
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` processes form data without verifying a CSRF token. This exposes the application to Cross-Site Request Forgery attacks, allowing malicious sites to submit expenses on behalf of authenticated users.
**Action:** Install `Flask-WTF`, configure `CSRFProtect` in `app.py`, and include a hidden CSRF token field in the expense form.

## High Severity

### 2. Unsafe Input Validation (Infinity/NaN)
The `add_expense` route uses `float(amount_str)` which accepts `Infinity` and `NaN` values. Since `float('inf') > 0` is true, this bypasses the validation logic in `ExpenseService`, potentially allowing invalid or malicious data into the system.
**Action:** Update input validation to strictly reject non-finite numbers using `math.isfinite(amount)` before calling the service.

### 3. Deviation from Data Persistence Requirements
The `InMemoryExpenseRepository` uses a Python `list` for storage, whereas the requirements explicitly mandate `sqlite:///:memory:`. Using a list fails to validate that the data model is compatible with SQL constraints and differs from the specified architecture.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database to comply with requirements and ensure SQL compatibility.

## Medium Severity

### 4. Hardcoded Secret Key
The application secret key is hardcoded as `"dev-secret-key"` in `app.py`. Hardcoding secrets in the source code compromises security and makes it difficult to rotate keys in production environments.
**Action:** Load the `SECRET_KEY` from environment variables (e.g., `os.environ.get("SECRET_KEY")`) and ensure the application fails to start if it is missing in production.

### 5. Debug Mode Enabled in Entry Point
The `app.py` entry point enables `debug=True` within the `if __name__ == "__main__":` block. If this file is executed directly in a production environment (e.g., inside a container), it exposes the interactive debugger and sensitive information.
**Action:** Disable debug mode by default or control it via an environment variable (e.g., `debug=os.environ.get("FLASK_DEBUG", "0") == "1"`).

### 6. Test Configuration Discrepancies
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`) and explicitly disable CSRF protection (`WTF_CSRF_ENABLED = False`). This differs from `app.py` (prefix `/expenses`) and masks the lack of CSRF handling in the actual application.
**Action:** Update tests to use the `create_app` factory or match the production configuration (url_prefix) and enable/test CSRF protection.

## Low Severity

### 7. Mixed Language in User Feedback
The `ExpenseService` raises exceptions with English (or mixed) messages which are flashed directly to the user in `routes.py`. The requirements state "UI/Felmeddelanden på Svenska". Flashing internal exception messages can lead to inconsistent or untranslated user feedback.
**Action:** Catch specific exceptions in the route and flash dedicated Swedish error messages, or ensure service exceptions contain only the Swedish message meant for the UI.
