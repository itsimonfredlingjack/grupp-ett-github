## High Severity

### 1. Missing CSRF Protection (Security)
The `POST /add` route in `src/expense_tracker/presentation/routes.py` processes form data without any CSRF protection. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Recommendation:** Integrate `Flask-WTF`'s `CSRFProtect` and use it to protect all POST forms.

## Medium Severity

### 2. Debug Mode Enabled in Production (Security)
The `app.py` file configures `app.run(debug=True)` in the `__main__` block. While this is wrapped in `if __name__ == "__main__":`, `create_app` also doesn't explicitly disable it for production.
**Recommendation:** Ensure `debug` mode is controlled via environment variables and defaults to `False` in production contexts.

### 3. Deviation from Storage Requirement (Correctness)
The Jira requirement specifies "DB: sqlite:///:memory: (InMemoryRepository)". The current implementation of `InMemoryExpenseRepository` uses a Python list (`self._expenses = []`). While functional for an MVP, this deviates from the technical specification.
**Recommendation:** Implement the repository using `sqlite3` with an in-memory database to match the requirements, or update the requirements to reflect the list-based implementation.

## Low Severity

### 4. Test Configuration Mismatch (Reliability)
In `tests/expense_tracker/test_routes.py`, the blueprint is registered at the root `/`. However, in `app.py`, it is registered with `url_prefix="/expenses"`. This discrepancy means tests are not verifying the actual routing configuration used in the application.
**Recommendation:** Update tests to use the same prefix or use the `create_app` factory to ensure configuration consistency.

### 5. Hardcoded Secret Key (Security)
The application uses a hardcoded secret key `app.secret_key = "dev-secret-key"` in `app.py`.
**Recommendation:** Load the secret key from an environment variable and fail if it is missing in production.
