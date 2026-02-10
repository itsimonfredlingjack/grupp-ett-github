# PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`admin`/`admin123`). This allows anyone with access to the source code to gain admin privileges.
**Action:** Move credentials to environment variables or a secure database.

### 2. Authentication Bypass Vulnerability (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` accepts any token starting with `token_`. Attackers can bypass authentication by sending a header like `Authorization: Bearer token_fake`.
**Action:** Implement proper token validation using JWT or server-side session storage.

## High Severity

### 3. Missing CSRF Protection (Security)
The subscription form in `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html` uses a raw HTML form without CSRF tokens. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Use Flask-WTF forms to automatically include and validate CSRF tokens.

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated, allowing unauthorized users to inject events or reset the dashboard.
**Action:** Implement authentication (e.g., API key or AdminAuthService) for all monitoring endpoints.

### 5. Missing Dependency: python-dotenv (Reliability)
`python-dotenv` is listed in `pyproject.toml` but missing from `requirements.txt`. This may cause deployment failures or environment variable loading issues in production.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.

## Medium Severity

### 6. Unsafe Application Configuration (Security)
The application is configured with `debug=True` and `allow_unsafe_werkzeug=True` in the main block of `app.py`. This is unsafe for production deployments.
**Action:** Configure these settings via environment variables and ensure they are disabled in production.

## Low Severity

### 7. Hardcoded CSS Styles (Maintainability)
The `subscribe.html` template includes embedded CSS within a `<style>` block. This violates separation of concerns and prevents caching.
**Action:** Move styles to `src/sejfa/newsflash/presentation/static/css/style.css`.

### 8. Weak Secret Key Configuration (Security)
The `app.secret_key` falls back to "dev-secret-key" if the environment variable is not set.
**Action:** Ensure the application fails to start or logs a critical warning if `SECRET_KEY` is missing in production.
