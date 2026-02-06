# PR Review Findings

## Critical Severity

### 1. Insecure Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token starting with `"token_"` as valid. This allows attackers to bypass authentication by sending a forged header like `Authorization: Bearer token_fake`.
**Action:** Implement proper token validation (e.g., using JWT or server-side session storage) to ensure tokens are legitimate and issued by the server.

## High Severity

### 2. Hardcoded Admin Credentials (Security)
The `AdminAuthService` contains hardcoded credentials (`admin`/`admin123`). If exposed or deployed, this grants unauthorized administrative access.
**Action:** Move credentials to environment variables or a secure database, and use password hashing.

### 3. Hardcoded Secret Key (Security)
The application uses a hardcoded `SECRET_KEY` ("dev-secret-key") in `app.py` without checking environment variables. This compromises session security in production.
**Action:** Update `app.py` to load `SECRET_KEY` from `os.environ` with a fallback only for development.

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using a dedicated API key or the `AdminAuthService` (once fixed).

## Medium Severity

### 5. Incomplete Refactor: Code Duplication (Maintainability)
The repository contains duplicate `SubscriptionService` implementations in `src/sejfa/cursorflash/business/` and `src/sejfa/newsflash/business/`. The `cursorflash` version is still used by legacy tests and routes, despite the intention to migrate to `newsflash`.
**Action:** Remove `src/sejfa/cursorflash/business/subscription_service.py` and migrate or remove the corresponding tests and routes in `cursorflash` and `tests/cursorflash/`.

### 6. Permissive CORS Policy for WebSockets (Security)
The `SocketIO` instance in `app.py` is initialized with `cors_allowed_origins="*"`. This allows any site to connect to the WebSocket server, potentially enabling Cross-Site WebSocket Hijacking (CSWSH).
**Action:** Restrict `cors_allowed_origins` to trusted domains (e.g., via environment variable) in production.
