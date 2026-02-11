# PR Review Findings

## High Severity

### 1. Hardcoded Secret Key (Security)
The `create_app` function in `app.py` sets `app.secret_key = "dev-secret-key"` without checking for an environment variable override. This makes the session cookies vulnerable if deployed.
**Action:** Update `app.py` to use `os.environ.get("SECRET_KEY", "dev-secret-key")` and ensure a unique key is set in production.

### 2. Missing Dependency: python-dotenv (Reliability)
`python-dotenv` is listed in `pyproject.toml` but missing from `requirements.txt`. Since CI/CD workflows use `requirements.txt`, this inconsistency can lead to environment issues.
**Action:** Add `python-dotenv>=1.0.0` to `requirements.txt`.

## Medium Severity

### 3. Unprotected Monitoring Endpoints (Security)
The monitoring endpoints in `src/sejfa/monitor/monitor_routes.py` (e.g., `POST /api/monitor/state`) are unauthenticated. This allows any network user to inject false events or reset the dashboard state.
**Action:** Implement authentication for these endpoints, potentially using the existing `AdminAuthService` or a dedicated API key.

### 4. Inaccurate System Status (Correctness)
The documentation in `docs/AGENTIC_DEVOPS_LOOP.md` contains inaccuracies regarding the codebase:
- It states `scripts/preflight.sh` is missing, but it exists and is executable.
- It states `start-task/SKILL.md` writes to the "wrong" `CURRENT_TASK.md`, but it correctly writes to the root file.
- It lists `docs/DEPLOYMENT.md` which has been deleted.
**Action:** Update `docs/AGENTIC_DEVOPS_LOOP.md` to accurately reflect the codebase state.

## Low Severity

### 5. Broken Documentation Reference (Correctness)
`docs/DEPLOYMENT.md` is referenced in `docs/AGENTIC_DEVOPS_LOOP.md`, `README.md`, and `.claude/CLAUDE.md`, but the file has been deleted in this PR.
**Action:** Remove the references to `docs/DEPLOYMENT.md` in all documentation files or restore the file.

### 6. Unsafe Application Configuration (Security)
The `app.py` file enables `allow_unsafe_werkzeug=True` and `debug=True` in the main block. While this is guarded by `if __name__ == "__main__":`, it encourages unsafe practices.
**Action:** Ensure these settings are disabled in production environments.
