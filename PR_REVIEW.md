# Code Review for scripts/jules_payload.py

## Security

### Weak Secret Masking
**Severity: High**
The current `MASK_RULES` regex only accounts for shell-style variable assignments (`VAR=VAL`) and HTTP headers. It fails to detect and redact secrets in JSON or YAML files (e.g., `"api_key": "secret"` or `key: secret`), which are common in configuration files.
**Actionable:** Update `MASK_RULES` to support JSON/YAML separators (`[:=]`) and optional quotes. Example: `(?i)"?[\w]*(token|secret|password|key)[\w]*"?\s*[:=]\s*"?[\w\-+/=]{8,}"?`

## Reliability

### Unhandled Git Renames
**Severity: Medium**
`git diff --numstat` can output rename syntax (e.g., `{old => new}`) which the current parsing logic does not handle. This results in incorrect paths being passed to subsequent `git diff` commands, causing them to fail or return empty content.
**Actionable:** Add `--no-renames` to all `git diff` commands (e.g., in `changed_file_stats`) to ensure stable, deterministic file paths.

### Silent Git Failures
**Severity: Medium**
The `run_git` function swallows all errors by returning an empty string when `returncode != 0`. If git fails (e.g., due to safe directory limits or missing history), the payload generation will fail silently, resulting in an empty context for the agent.
**Actionable:** Raise a `PayloadError` or log a warning to stderr when critical git commands fail.

## Correctness

### Unhandled Quoted Paths
**Severity: Low**
Git quotes filenames that contain spaces or special characters (e.g., `"path/to/my file.py"`). The current `split("\t")` logic in `changed_file_stats` does not handle unquoting, leading to incorrect path lookups and exclusions.
**Actionable:** Use `git diff -z` (null-terminated output) or set `-c core.quotepath=false` in the git command arguments to handle complex paths reliably.
