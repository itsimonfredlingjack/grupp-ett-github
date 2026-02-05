# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection (Security)
The `POST /add` endpoint lacks CSRF protection. The test configuration explicitly disables it (`app.config["WTF_CSRF_ENABLED"] = False`), and there is no evidence of `Flask-WTF` or manual CSRF token handling in `src/expense_tracker/presentation/routes.py` or the template `add.html`.
**Action:** Implement `Flask-WTF` forms with CSRF tokens in `routes.py` and templates.

## High Severity

### 2. Hardcoded Secret Key (Security)
The application uses a hardcoded secret key `app.secret_key = "dev-secret-key"` in `app.py`. This poses a significant security risk if deployed to production.
**Action:** Use `os.environ.get("SECRET_KEY")` with a fallback only for local development, or enforce environment variables.

## Medium Severity

### 3. Repository Implementation Mismatch (Correctness)
The requirements specified using `sqlite:///:memory:` for the `InMemoryExpenseRepository`, but the implementation in `src/expense_tracker/data/repository.py` uses a Python `list`.
**Action:** Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database to match requirements and better simulate SQL behavior.

## Low Severity

### 4. Test Route Configuration Discrepancy (Reliability)
The integration tests in `tests/expense_tracker/test_routes.py` register the blueprint at the root (`/`), whereas `app.py` registers it at `/expenses`. This might mask path-related issues (e.g., hardcoded links) in the templates.
**Action:** Update the test fixture to register the blueprint at `/expenses` to match production configuration.
