## High Severity

### 1. Missing CSRF Protection (Security)
The `add_expense` route and form lack CSRF protection. The form in `src/expense_tracker/templates/expense_tracker/index.html` does not include a CSRF token, and the route in `src/expense_tracker/presentation/routes.py` does not validate it. This leaves the application vulnerable to Cross-Site Request Forgery attacks.

**Recommendation**: Use Flask-WTF forms which handle CSRF automatically, or explicitly add a hidden CSRF token field to the form and ensure the route validates it.

## Medium Severity

### 2. Insecure Persistence Implementation (Correctness)
The `InMemoryExpenseRepository` in `src/expense_tracker/data/repository.py` uses a Python list (`self._expenses = []`) for storage, but the requirements in `CURRENT_TASK.md` explicitly specified `sqlite:///:memory:`. This deviation from technical requirements affects future extensibility and SQL compatibility.

**Recommendation**: Update `InMemoryExpenseRepository` to use `sqlite3` with an in-memory database as required.

### 3. Test Setup Bypasses App Factory (Reliability)
The `app` fixture in `tests/expense_tracker/test_routes.py` manually constructs a `Flask` instance instead of using the `create_app` factory defined in `app.py`. This bypasses global configuration, error handlers, and middleware, leading to tests that may not accurately reflect the production environment.

**Recommendation**: Update the test fixture to import and use `create_app()`.

## Low Severity

### 4. CSRF Protection Disabled in Tests (Security/Testing)
The test configuration in `tests/expense_tracker/test_routes.py` explicitly disables CSRF protection (`app.config["WTF_CSRF_ENABLED"] = False`). This practice hides the security vulnerability in the implementation (Finding #1) and prevents tests from verifying security controls.

**Recommendation**: Enable CSRF in tests and update test clients to handle CSRF tokens.

### 5. Inaccurate Test Route Registration (Correctness)
Integration tests register the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. This discrepancy means the tests do not verify the actual URL structure and routing logic used in the application.

**Recommendation**: Register the blueprint at `/expenses` in the test setup to match the application configuration.
