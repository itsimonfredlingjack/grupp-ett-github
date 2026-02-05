# PR Review Findings

## Critical Severity

### 1. Broken Authentication Logic (Security)
The `AdminAuthService.validate_session_token` method in `src/sejfa/core/admin_auth.py` insecurely validates tokens by only checking if they start with `"token_"`. This allows attackers to bypass authentication by providing any string with that prefix.
**Action:** Implement proper token validation (e.g., using a secure store or JWT signature verification).

### 2. Missing Authentication on Monitor Endpoints (Security)
The monitoring endpoints (`/api/monitor/state`, `/reset`, `/task`) in `src/sejfa/monitor/monitor_routes.py` are publicly accessible without any authentication. This allows unauthorized users to manipulate the workflow state.
**Action:** Apply the `@require_admin_token` decorator or a dedicated monitoring token check to all monitoring endpoints.

### 3. Stored XSS in Dashboard (Security)
The `monitor.html` file renders `event.message` using `innerHTML` (via `updateEventLog`) without sanitization. Since the state update endpoint is unauthenticated, an attacker can inject malicious scripts that execute in the dashboard viewer's browser.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input using a library like DOMPurify.

## High Severity

### 4. State Synchronization Failure (Reliability)
The `MonitorService` stores state in memory (`self.nodes`), but the `Dockerfile` configures `gunicorn` with 4 workers. This causes a "split-brain" scenario where each worker maintains its own isolated state, leading to inconsistent dashboard updates.
**Action:** Move monitoring state to a shared external store (e.g., Redis) to ensure consistency across workers.

### 5. Hardcoded Secrets and Credentials (Security)
The application uses a hardcoded `SECRET_KEY` ("dev-secret-key") and admin credentials (`username="admin"`, `password="admin123"`) in `app.py` and `src/sejfa/core/admin_auth.py`. This compromises session security and allows unauthorized access in production.
**Action:** Load sensitive values from environment variables and ensure the application fails if they are missing in production.

### 6. Missing CSRF Protection (Security)
The application lacks global Cross-Site Request Forgery (CSRF) protection. Endpoints like `/admin/subscribers` and `/expenses/add` process state-changing requests without CSRF tokens.
**Action:** Initialize `Flask-WTF`'s `CSRFProtect` in `app.py` and ensure all forms include the CSRF token.

## Medium Severity

### 7. Race Conditions in MonitorService (Reliability)
The `MonitorService.update_node` method modifies shared dictionaries (`self.nodes`) without locking. In a threaded environment (e.g., `socketio` with threading), this can lead to race conditions and data corruption.
**Action:** Add a `threading.Lock` to protect concurrent access to shared state in `MonitorService`.

### 8. In-Memory Persistence (Reliability)
The `InMemoryExpenseRepository` uses a Python list for storage, which results in data loss upon application restart. This is unsuitable for production use.
**Action:** Implement a persistent repository (e.g., `SQLAlchemyRepository` backed by PostgreSQL or SQLite).
