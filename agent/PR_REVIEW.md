# PR Review Findings

## High Severity

### 1. Hardcoded Secret Key (Security)
The application `app.secret_key` is hardcoded to "dev-secret-key" in `app.py`. This poses a significant security risk if deployed.
**Action:** Configure the application to load `SECRET_KEY` from an environment variable in production.

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 3. Generated Artifact Committed (Maintainability)
The file `coverage.xml` is a generated coverage report and should not be committed to the repository. It bloats the history and changes frequently.
**Action:** Add `coverage.xml` to `.gitignore` and remove it from the PR.

## Low Severity

### 4. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 5. Deprecated `datetime.utcnow()` Usage (Maintainability)
The `monitor_routes.py` file uses `datetime.utcnow()`, which is deprecated in Python 3.12+.
**Action:** Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.
