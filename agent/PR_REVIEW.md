# PR Review Findings

## Critical Severity

### 1. Unauthenticated Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication (e.g., `AdminAuthService` or API key) for these endpoints.

## High Severity

### 2. Stored XSS in `monitor.html` (Security)
The `static/monitor.html` dashboard renders `event.message` and `event.node` using `innerHTML` without sanitization. This allows an attacker to inject malicious scripts via the unauthenticated monitoring API.
**Action:** Use `textContent` instead of `innerHTML` or sanitize the input before rendering.

### 3. Potential Import Error in Hooks (Reliability)
The hooks `.claude/hooks/stop-hook.py` and `monitor_hook.py` attempt to import `monitor_client` directly. When run from the repository root (as is standard for hooks), this import may fail if `.claude/hooks` is not in `PYTHONPATH`.
**Action:** Add `sys.path.append(os.path.dirname(__file__))` before the import.

## Medium Severity

### 4. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. This poses a security risk if the application is executed directly in production.
**Action:** Use environment variables (e.g., `FLASK_DEBUG`) or ensure these settings are only enabled in local development.

### 5. Missing Implementation in Active Module (Correctness)
The active application uses the `newsflash` module, but `src/sejfa/newsflash/presentation/static/css/style.css` still contains the old color scheme (`#0a0e1a`, `#3b82f6`) instead of the new one (`#1a1d29` -> `#0f1117`).
**Action:** Update the CSS variables to match the new design requirements.

### 6. Missing Execution Permissions on Hooks (Reliability)
The scripts `.claude/hooks/stop-hook.py` and `.claude/hooks/monitor_hook.py` lack executable permissions (`chmod +x`). This may prevent them from being executed as hooks by the agent environment.
**Action:** Run `chmod +x .claude/hooks/stop-hook.py .claude/hooks/monitor_hook.py`.

### 7. Missing Test Coverage for Monitor Hook (Test Coverage)
There are no tests for `.claude/hooks/monitor_hook.py`. While `stop-hook.py` is well-tested, the monitor hook logic is unverified and could fail silently.
**Action:** Add unit tests for `monitor_hook.py` covering tool-to-node mapping logic.

## Low Severity

### 8. Hardcoded Coverage Threshold (Maintainability)
The coverage threshold is hardcoded to `80` in `.github/workflows/ci.yml`, duplicating the configuration in `.claude/ralph-config.json`. This can lead to inconsistency.
**Action:** Centralize the configuration or ensure they are kept in sync.
