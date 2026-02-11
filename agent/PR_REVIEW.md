# Automated PR Review Findings

## High Severity

### 1. Split-Brain Monitoring State (Reliability)
The `MonitorService` stores state in-memory, but the `Dockerfile` configures `gunicorn` with 4 workers. This causes a "split-brain" issue where monitoring updates are isolated to a single worker and not shared across processes, leading to inconsistent dashboard state.
**Action:** Use an external store (e.g., Redis) for state or configure gunicorn to use a single worker (with async workers if needed).

### 2. Duplicate Task Memory (Correctness)
The repository contains two conflicting task memory files: the root `CURRENT_TASK.md` and `docs/CURRENT_TASK.md`. This violates the single source of truth principle and risks agent confusion.
**Action:** Unify the task state in the root `CURRENT_TASK.md` and delete `docs/CURRENT_TASK.md`.

## Medium Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `/api/monitor/state`) are unauthenticated. This allows unauthorized actors to inject fake events or reset the monitoring state, potentially disrupting operations.
**Action:** Implement authentication (e.g., API key or shared secret) for these endpoints.

### 4. Redundant Documentation (Maintainability)
The file `docs/Bygga Agentic Dev Loop-system.md` appears to be a Swedish translation of `docs/AGENTIC_DEVOPS_LOOP.md`, creating maintenance overhead and potential for out-of-sync documentation.
**Action:** Delete `docs/Bygga Agentic Dev Loop-system.md` and maintain English as the single documentation language.

## Low Severity

### 5. Dead Code in Tests (Maintainability)
The helper method `extract_hex_color` in `tests/newsflash/test_color_scheme.py` is defined but never used, as tests use inline regex logic.
**Action:** Remove the unused `extract_hex_color` method.

### 6. Hardcoded Secret Key (Security)
The `app.py` file sets `app.secret_key = "dev-secret-key"` without an environment variable override mechanism for production, posing a security risk if deployed as-is.
**Action:** Update `app.py` to use `os.environ.get("SECRET_KEY", "dev-secret-key")`.
