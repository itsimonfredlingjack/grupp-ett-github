# PR Review: 134

**Review Summary:**
The PR implements the ExpenseTracker MVP with Clean Architecture and meets the functional requirements. However, there are security and reliability findings that should be addressed.

## High Severity

### 1. Missing CSRF Protection (Security)
The expense submission form in `src/expense_tracker/templates/expense_tracker/index.html` and the `add_expense` route in `src/expense_tracker/presentation/routes.py` lack CSRF protection. This makes the application vulnerable to Cross-Site Request Forgery attacks.
**Recommendation:** Enable CSRF protection (e.g., using Flask-WTF) and include the CSRF token in the form.

## Medium Severity

### 2. Missing Test for Non-Numeric Input (Reliability)
`tests/expense_tracker/test_routes.py` lacks a specific test case for non-numeric input in the 'amount' field. While the implementation handles `ValueError`, explicit test coverage ensures this error handling remains intact.
**Recommendation:** Add a test case in `TestAddRoute` that submits a non-numeric string for 'amount' and asserts the error message.

## Low Severity

### 3. Test Configuration Discrepancy (Testing)
`tests/expense_tracker/test_routes.py` registers the blueprint at the root (`/`), while `app.py` registers it at `/expenses`. Integration tests are not testing the actual URL structure used in production.
**Recommendation:** Update test setup to register at `/expenses` or document this discrepancy.

### 4. Hardcoded Secret Key (Best Practice)
`app.py` sets `app.secret_key = "dev-secret-key"`. While acceptable for dev, this is a security risk if deployed.
**Recommendation:** Ensure the secret key is loaded from an environment variable in production.
