# Jules PR Review

## Findings

### 1. File Organization Violation (Medium Severity)
**File:** `PR_REVIEW.md`

**Observation:** The file `PR_REVIEW.md` is added to the root directory.

**Rule:** `CONTRIBUTING.md` states: "Keep the root directory clean. Only `app.py`, `CURRENT_TASK.md` (agent memory), and config files should be here."

**Recommendation:**
- Move review artifacts to a dedicated directory (e.g., `agent/reviews/`) or ensure they are not committed if they are transient.
