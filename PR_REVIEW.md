# Jules PR Review

## Findings

### 1. File Organization Violation (Low Severity)
**File:** `TEST_JULES.md`

**Observation:** The file `TEST_JULES.md` is added to the root directory.

**Rule:** `CONTRIBUTING.md` states: "Keep the root directory clean. Only `app.py`, `CURRENT_TASK.md` (agent memory), and config files should be here."

**Recommendation:**
- If this is a test artifact, consider moving it to `tests/` or `docs/`.
- If it is a temporary trigger, ensure it is removed before merging or add it to `.gitignore`.
