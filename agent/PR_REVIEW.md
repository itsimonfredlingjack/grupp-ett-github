# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection & Dependency
The application lacks Cross-Site Request Forgery (CSRF) protection. `Flask-WTF` is missing from `requirements.txt`, `CSRFProtect` is not initialized in `app.py`, and the expense form lacks the CSRF token.
**Action:** Add `Flask-WTF` to `requirements.txt`, initialize `CSRFProtect(app)`, and add `{{ csrf_token() }}` to forms.

## High Severity

### 2. Missing Production Dependency (Reliability)
`flask-socketio` is imported in `app.py` but missing from `requirements.txt`. This will cause the application to crash in production environments (e.g., Docker) where packages are installed strictly from requirements.
**Action:** Add `flask-socketio` to `requirements.txt`.

### 3. Inappropriate Data Type for Currency (Correctness)
The `Expense` model and service use `float` for the `amount` field. Floating-point arithmetic is imprecise for currency calculations.
**Action:** Use `decimal.Decimal` for monetary values in models and calculations.

### 4. Hardcoded Secret Key (Security)
The application uses a hardcoded `secret_key` ("dev-secret-key") in `app.py`. This compromises session security.
**Action:** Use `os.environ.get("SECRET_KEY")` and enforce a strong key in production.

## Medium Severity

### 5. Input Validation Flaw (Correctness)
The route uses `float(amount_str)` which accepts `infinity` and `NaN`. This bypasses the `amount > 0` validation if `inf` is passed (since `inf > 0` is true).
**Action:** Validate that the input is a finite number or use `Decimal` with strict validation before logic checks.

### 6. Deviation from Persistence Requirements
The `InMemoryExpenseRepository` uses a Python `list` instead of `sqlite:///:memory:` as originally specified. This lacks SQL constraint validation and differs from a production DB behavior.
**Action:** Implement `sqlite3` based repository or explicit acceptance of list-based storage.

## Low Severity

### 7. Test Configuration Mismatch
Integration tests register the blueprint at `/` while `app.py` registers it at `/expenses`. This mismatch can hide path-related bugs.
**Action:** Update tests to use the correct url prefix or use `create_app`.

### 8. CSRF Disabled in Tests
Tests explicitly disable CSRF (`WTF_CSRF_ENABLED = False`), masking the absence of protection in the actual code.
**Action:** Enable CSRF in tests and ensure forms include tokens to verify security controls.
