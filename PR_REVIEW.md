# Code Review for scripts/jules_payload.py

## Security

### [Critical] Secrets redaction regex fails on quoted values
**Location**: `MASK_RULES` definition
**Severity**: High

The regex used for masking secrets is:
```python
r"(?i)\b([A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY)[A-Z0-9_]*)\s*=\s*[^\s'\"]+"
```
The character class `[^\s'\"]+` specifically excludes single (`'`) and double (`"`) quotes. This means that if a secret is assigned as a quoted string (e.g., `API_KEY="my-secret-value"`), the regex will **fail to match** the value part, and the secret will **not be redacted**.

**Recommendation**:
Modify the regex to handle optional quotes. For example:
```python
r"(?i)\b([A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY)[A-Z0-9_]*)\s*=\s*['\"]?([^'\"\s]+)['\"]?"
```
Or simply allow matching the value until whitespace if appropriate, or use a more robust parser.

## Reliability

### [Major] `run_git` silently suppresses errors
**Location**: `run_git` function
**Severity**: Medium

The `run_git` function catches non-zero exit codes and returns an empty string without logging the error or raising an exception:
```python
if result.returncode != 0:
    return ""
```
This behavior can hide critical failures (e.g., git config issues, missing git binary, permission errors) and lead to valid but empty or partial payloads being generated, which might confuse the downstream agent or workflow.

**Recommendation**:
Raise an exception (e.g., `PayloadError`) or log the error to `stderr` so that the workflow can fail fast or at least report the issue.

## Performance

### [Minor] Inefficient `Path` object creation in loop
**Location**: `is_excluded_path` function
**Severity**: Low

The function creates a `Path` object for every file checked:
```python
return Path(normalized).suffix.lower() in BINARY_EXTENSIONS
```
Since this function is likely called for every file in the repository (potentially thousands), creating a `Path` object is overhead.

**Recommendation**:
Use string manipulation:
```python
return normalized.lower().endswith(tuple(BINARY_EXTENSIONS))
```
Note: `BINARY_EXTENSIONS` should be converted to a tuple if it isn't already, or `endswith` can accept the set if converted. (Python `endswith` requires a tuple).
