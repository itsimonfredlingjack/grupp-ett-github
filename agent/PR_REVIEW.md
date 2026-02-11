# PR Review Findings

## Critical Severity

### 1. Inconsistent Dependency: python-dotenv (Correctness)
The file `pyproject.toml` lists `python-dotenv` as a dependency, but it is missing from `requirements.txt`. The scripts `scripts/preflight.sh` and `.claude/skills/finish-task/SKILL.md` rely on `dotenv`. This inconsistency will cause failures in environments set up via `requirements.txt`.
**Action:** Add `python-dotenv` to `requirements.txt` to match `pyproject.toml`.

## Medium Severity

### 2. Hardcoded Virtual Environment Path (Reliability)
The skill `.claude/skills/finish-task/SKILL.md` hardcodes the virtual environment path as `venv/bin/activate`. This assumption makes the skill fragile if the user uses a different virtual environment directory (e.g., `.venv`) or a different activation method.
**Action:** Use a more robust method to detect the virtual environment, or explicitly document this requirement.
