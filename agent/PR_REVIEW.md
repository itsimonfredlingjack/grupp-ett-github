# PR Review Findings

## Critical Severity

### 1. Missing CSRF Protection on Expense Form (Security)
The `POST /add` endpoint in `src/expense_tracker/presentation/routes.py` lacks CSRF protection. `Flask-WTF` is not initialized in `app.py`, and the form integration lacks `csrf_token`. Tests explicitly disable CSRF (`WTF_CSRF_ENABLED = False`), masking this vulnerability.
**Action:** Add `Flask-WTF` to `requirements.txt`. Initialize `CSRFProtect` in `app.py`. Use `form.hidden_tag()` in templates. Enable CSRF in tests and update them to pass tokens.

## High Severity

### 2. Deviation from Persistence Requirements (Correctness)
The `InMemoryExpenseRepository` implementation uses a Python `list`, but the requirements specified `sqlite:///:memory:`. This fails to test SQL constraints and behavior, which is critical for future persistence layers.
**Action:** Reimplement `InMemoryExpenseRepository` to use `sqlite3` (or `SQLAlchemy` with SQLite in-memory).

## Medium Severity

### 3. Hardcoded Secret Key (Security)
`app.py` uses a hardcoded secret key (`"dev-secret-key"`). This is insecure for production.
**Action:** Use `python-dotenv` to load `SECRET_KEY` from environment variables, defaulting to a secure random value only in development.

### 4. Missing Dependencies (Reliability)
`flask-socketio`, `python-dotenv`, and `Flask-WTF` are required but missing from `requirements.txt`. This causes runtime failures in fresh environments.
**Action:** Add `flask-socketio>=5.0.0`, `python-dotenv>=1.0.0`, and `Flask-WTF>=1.0.0` to `requirements.txt`.

### 5. Floating Point Precision for Currency (Correctness)
The `Expense` model uses `float` for `amount`. Floating point arithmetic can lead to precision errors in financial calculations.
**Action:** Use `decimal.Decimal` for the `amount` field in `Expense` model and service.

## Low Severity

### 6. Inconsistent Test Configuration (Reliability)
Integration tests register the blueprint at `/`, while `app.py` registers it at `/expenses`. This masks potential path-related issues.
**Action:** Update tests to register the blueprint at `/expenses` to match production configuration.

### 7. Input Validation Edge Cases (Correctness)
The `float()` conversion accepts `Infinity` and `NaN` (if not caught). `amount > 0` validation allows `Infinity`.
**Action:** Add checks to ensure `amount` is finite using `math.isfinite()`.
