# PR Review Findings

## High Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 2. Incomplete Refactor: Code Duplication (Maintainability)
The repository contains duplicate `SubscriptionService` implementations in `src/sejfa/cursorflash/business/` and `src/sejfa/newsflash/business/`. Although the intention was to move the service to `newsflash`, the `cursorflash` version remains and is still used by legacy tests.
**Action:** Remove `src/sejfa/cursorflash/business/subscription_service.py` and migrate or remove the corresponding tests in `tests/cursorflash/`.
