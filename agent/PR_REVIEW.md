# PR Review Findings

## Critical Severity

### 1. Unjustified Test Deletion (Correctness)
The PR deletes valid and passing tests: `tests/newsflash/test_subscription_service.py` and `tests/newsflash/test_integration.py`. These tests are essential for verifying the `SubscriptionService` logic and integration, introduced in commit `afb64fb`. Deleting them significantly reduces test coverage and correctness assurance.
**Action:** Restore the deleted test files immediately.

## High Severity

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 3. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. Additionally, `app.secret_key` is hardcoded to `"dev-secret-key"`. While acceptable for local development, these pose risks if deployed to production.
**Action:** Ensure these settings are disabled or securely configured in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`, `SECRET_KEY`).
