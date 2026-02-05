# PR Review: GE-32 News Flash App

**Review Summary:**
The implementation of the News Flash App follows the 3-layer architecture well and passes functional tests. However, there are significant issues regarding project structure (Clean Root Policy), security (unsafe HTTP methods), and test coverage configuration that need to be addressed.

## Correctness
### 1. Clean Root Policy Violation (High)
**Issue:** The `newsflash_app` directory is located in the repository root. `CONTRIBUTING.md` explicitly states: "Code must be organized into `src/`... Keep the root directory clean."
**Action Required:** Move `newsflash_app` to `src/newsflash_app`.

## Security Regressions
### 2. Unsafe Method for State Change (High)
**Issue:** The route `@bp.route("/delete/<int:item_id>", methods=["GET"])` allows state modification via GET requests. This violates HTTP semantics and exposes the application to CSRF attacks and accidental deletions by web crawlers.
**Action Required:** Change the route to use `POST` (or `DELETE`) and update the template/tests accordingly.

## Reliability and Edge Cases
### 3. Ephemeral Data Persistence (Medium)
**Issue:** `InMemoryNewsFlashRepository` is instantiated inside `create_app()`. Since it's not a singleton or shared resource, each application instance (and potentially each worker in a production WSGI setup) will have its own isolated data store. Data will be lost on restart.
**Note:** This is acceptable for the MVP phase ("Kör InMemoryRepository tills vidare") but should be documented as a limitation for deployment.

## Test Coverage Gaps
### 4. Coverage Configuration Mismatch (Medium)
**Issue:** The CI script `scripts/ci_check.sh` executes `pytest ... --cov=src --cov=app.py`. Because `newsflash_app` is not in `src`, it is excluded from coverage analysis during CI, despite being listed in `pyproject.toml`.
**Action Required:** Moving the code to `src/` (Correction #1) will automatically resolve this.

## Performance Risks
- No significant performance risks identified for the current scope.
