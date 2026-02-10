# PR Review Findings

## High Severity

### 1. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 2. Stored XSS Vulnerability (Security)
The `MonitorService` in `src/sejfa/monitor/monitor_service.py` stores unsanitized `message` content in `event_log`. If the frontend renders this using `innerHTML` (as indicated by memory/legacy code), it creates a Stored Cross-Site Scripting (XSS) vulnerability.
**Action:** Sanitize all inputs in `MonitorService` or ensure the frontend uses `textContent` / safe rendering methods.

## Medium Severity

### 3. Thread Safety Issues (Reliability)
`MonitorService` is not thread-safe. Methods like `update_node` and `add_event` modify shared state (`self.nodes`, `self.event_log`) without locking. In a multi-threaded Flask/Gunicorn environment, this can lead to race conditions and state corruption.
**Action:** Add `threading.Lock` to `MonitorService` to synchronize access to shared resources.

### 4. Deprecated DateTime Usage (Reliability)
`src/sejfa/monitor/monitor_service.py` uses `datetime.utcnow()`, which is deprecated in Python 3.12 and scheduled for removal.
**Action:** Replace with `datetime.now(datetime.UTC)` to ensure future compatibility.

## Low Severity

### 5. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While acceptable for local development, this poses a risk if deployed to production.
**Action:** Ensure these settings are disabled in production environments, preferably via environment variables (e.g., `FLASK_DEBUG`).

### 6. Robustness of JSON Parsing (Reliability)
`src/sejfa/monitor/monitor_routes.py` calls `request.get_json()` without `silent=True`. This can raise a 400 Bad Request error for malformed JSON, which, while handled by Flask, could be handled more gracefully or explicitly.
**Action:** Use `request.get_json(silent=True)` and handle `None` result, or wrap in a try-except block for `BadRequest`.
