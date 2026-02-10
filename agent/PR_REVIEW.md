# Automated PR Review Findings

## Critical Severity

### 1. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`admin` / `[REDACTED]`). This allows anyone with access to the source code to gain admin privileges.
**Action:** Move credentials to environment variables or a secure database.

### 2. Authentication Bypass Vulnerability (Security)
The `validate_session_token` method in `src/sejfa/core/admin_auth.py` accepts any token starting with `token_`. Attackers can bypass authentication by sending a header like `Authorization: [REDACTED]`.
**Action:** Implement proper token validation using JWT or server-side session storage.

## High Severity

### 3. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization. An attacker can inject malicious scripts via the `message` field in monitoring events.
**Action:** Use `textContent` or a sanitization library to safely render user input.

### 4. Missing CSRF Protection (Security)
The subscription form in `src/sejfa/newsflash/presentation/templates/newsflash/subscribe.html` uses a raw HTML form without CSRF tokens. This exposes the application to Cross-Site Request Forgery attacks.
**Action:** Use Flask-WTF forms to automatically include and validate CSRF tokens.

### 5. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated, allowing unauthorized users to inject events or reset the dashboard.
**Action:** Implement authentication (e.g., API key or AdminAuthService) for all monitoring endpoints.

### 6. Hardcoded Secret Key (Security)
The application `SECRET_KEY` in `app.py` is hardcoded to `[REDACTED]` without an environment variable fallback. This compromises session security in production.
**Action:** Use `os.getenv("SECRET_KEY")` to load the key from the environment.

## Medium Severity

### 7. Unsafe Application Configuration (Security)
The application is configured with `debug=True` and `allow_unsafe_werkzeug=True` in the main block of `app.py`. This is unsafe for production deployments.
**Action:** Configure these settings via environment variables and ensure they are disabled in production.

### 8. Missing Dependency: python-dotenv (Reliability)
`python-dotenv` is listed in `pyproject.toml` and used in `src/sejfa/integrations/jira_client.py` but missing from `requirements.txt`. This may cause deployment failures or environment variable loading issues in production.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.
