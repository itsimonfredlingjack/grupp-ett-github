# PR Review Findings

## Critical Severity

### 1. Wrong Module Modification / Dead Code (Correctness)
The PR adds `src/sejfa/cursorflash/presentation/templates/cursorflash/index.html` to a deprecated and removed module (`cursorflash`). The active newsletter implementation is `newsflash`. Modifications to `cursorflash` will not affect the running application and re-introduce dead code.
**Action:** Move the changes to the active `src/sejfa/newsflash` module and remove the `cursorflash` directory.

### 2. Stored XSS in Monitor Dashboard (Security)
The `static/monitor.html` file renders `event.message` using `innerHTML` without sanitization in the `updateEventLog` function. This allows an attacker to inject malicious scripts via the monitoring API.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering.

## High Severity

### 3. Hardcoded Admin Credentials (Security)
The `AdminAuthService` in `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`username`: 'admin', `password`: 'admin123'). This creates a critical security vulnerability if deployed.
**Action:** Replace hardcoded credentials with environment variables or a database-backed authentication system.

### 4. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

## Medium Severity

### 5. Inline CSS in Templates (Maintainability)
The new template `src/sejfa/cursorflash/presentation/templates/cursorflash/index.html` contains extensive inline CSS styles. This violates separation of concerns and complicates Content Security Policy (CSP) implementation.
**Action:** Move styles to an external CSS file (e.g., `src/sejfa/newsflash/presentation/static/css/style.css`).

## Low Severity

### 6. Missing Template Inheritance (Maintainability)
The new template does not extend the base layout (`base.html`), resulting in inconsistent branding and navigation compared to the rest of the application.
**Action:** Refactor the template to extend `base.html` and use blocks for content.

### 7. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 8. Hardcoded Secret Key (Security)
The application uses a hardcoded secret key (`"dev-secret-key"`) in `app.py` if not overridden by environment variables. This is insecure for production.
**Action:** Ensure the secret key is loaded exclusively from environment variables in production.
