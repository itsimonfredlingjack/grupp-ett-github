# PR Review Findings

## Security Regressions

### 1. Critical: CSRF Vulnerability in Delete Route
**File:** `newsflash_app/presentation/routes.py`
**Severity:** Critical
The deletion route is implemented as a `GET` request:
```python
@bp.route("/delete/<int:item_id>", methods=["GET"])
```
This allows Cross-Site Request Forgery (CSRF) attacks where visiting a malicious link can delete items without user consent.
**Action:** Change to `POST` or `DELETE` method. Ideally, implement a form with a CSRF token for the deletion action.

### 2. High: Insecure Specification
**File:** `CURRENT_TASK.md`
**Severity:** High
The task specification explicitly requests `Routes: ... GET /delete/<id>`. This requirement enforces a security vulnerability.
**Action:** Update the specification to require `POST /delete/<id>` to align with security best practices.

### 3. Medium: Missing CSRF Protection on Forms
**File:** `newsflash_app/presentation/routes.py`
**Severity:** Medium
There is no apparent CSRF token validation for the `POST /add` route. While `flask-wtf` is not used, a basic token check should be implemented for state-changing operations to prevent CSRF.
**Action:** Add CSRF protection (e.g., via `Flask-WTF` or manual token injection).

## Reliability and Edge Cases

### 4. Low: Hardcoded Business Limits
**File:** `newsflash_app/business/service.py`
**Severity:** Low
`MAX_ITEMS_PER_PAGE = 20` is hardcoded. While acceptable for MVP, this should be moved to configuration for maintainability.
**Action:** Consider moving to `app.config`.

## Correctness

The implementation correctly follows the 3-layer architecture (Data, Business, Presentation) as requested. Dependencies are correctly injected, ensuring testability.

## Test Coverage Gaps

Test coverage is excellent, with both unit tests for the service layer and integration tests for the Flask app covering valid and invalid inputs.
