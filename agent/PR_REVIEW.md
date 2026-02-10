# PR Review Findings

## Critical Severity

### 1. Stale Task Context (Correctness)
The `CURRENT_TASK.md` file indicates that task GE-39 is "To Do", but the codebase already contains the implementation for GE-39 (News Flash Presentation) and subsequent tasks. This discrepancy between documentation and code state can mislead agents and causing regressions or infinite loops.
**Action:** Update `CURRENT_TASK.md` to reflect the actual state of the repository, or clarify if a re-implementation is intended.

### 2. Authentication Bypass (Security)
The `AdminAuthService.validate_session_token` method accepts any token string starting with `token_` (e.g., `token_hacker`), allowing unauthorized access to admin endpoints.
**Action:** Implement proper token validation, such as checking against a stored set of active tokens or using signed JWTs.

### 3. Hardcoded Credentials (Security)
The `AdminAuthService` uses hardcoded credentials (`admin`/`admin123`) in the source code.
**Action:** Load credentials from environment variables and use a secure hash comparison.

## High Severity

### 4. Stored XSS in Monitor Dashboard (Security)
The `monitor_routes.py` endpoint accepts a `message` field which is rendered using `innerHTML` in `static/monitor.html` without sanitization. This allows Stored Cross-Site Scripting (XSS) attacks.
**Action:** Sanitize the `message` content before rendering, or use `textContent` instead of `innerHTML`.

### 5. Data Loss in Subscription Service (Reliability)
The `SubscriptionService.process_subscription` method validates and normalizes data but fails to persist it to any storage (database or file), resulting in immediate data loss.
**Action:** Implement persistence for subscriptions (e.g., to a database or the `SubscriberService`).

### 6. Unprotected Monitor Endpoints (Security)
The monitoring API endpoints (e.g., `POST /api/monitor/state`) are unauthenticated, allowing any network user to inject false events or reset the dashboard.
**Action:** Protect these endpoints with an API key or the existing `AdminAuthService`.

## Medium Severity

### 7. Unsafe Application Configuration (Security)
The `app.py` configuration enables `debug=True` and `allow_unsafe_werkzeug=True` in the main block, and uses a hardcoded `secret_key`.
**Action:** Disable debug mode and unsafe options in production, and load `secret_key` from an environment variable.

### 8. Concurrency State Issues (Reliability)
The `MonitorService` stores state in-memory (`self.nodes`), which causes "split-brain" issues when running with multiple Gunicorn workers and race conditions in threaded environments.
**Action:** Move state storage to an external store (e.g., Redis) or use a singleton process for the monitor service.
