# PR Review Findings

## High Severity

### 1. Hardcoded Secret Key (Security)
`app.py` sets `app.secret_key = "dev-secret-key"` in `create_app()`. This default is insecure for production.
**Action:** Load `SECRET_KEY` from environment variables and fail if missing in production.

### 2. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 3. Global CORS Configuration (Security)
The `app.py` file initializes `SocketIO(app, cors_allowed_origins="*")`, effectively disabling CORS protection for real-time connections.
**Action:** Restrict `cors_allowed_origins` to trusted domains.

### 4. Incomplete Refactor: Code Duplication (Maintainability)
The repository contains duplicate `SubscriptionService` implementations in `src/sejfa/cursorflash/business/` and `src/sejfa/newsflash/business/`. Although the intention was to move the service to `newsflash`, the `cursorflash` version remains.
**Action:** Remove `src/sejfa/cursorflash/business/subscription_service.py` and migrate or remove the corresponding tests in `tests/cursorflash/`.

## Low Severity

### 5. Deprecated Date Usage (Correctness)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` and endpoints in `src/sejfa/monitor/monitor_routes.py` use the deprecated `datetime.utcnow()` method.
**Action:** Replace with `datetime.now(datetime.timezone.utc)`.
