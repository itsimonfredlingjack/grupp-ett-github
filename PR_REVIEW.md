# PR Review: scripts/jules_payload.py

## High Severity

1. **Security: Incomplete Authorization Header Masking**
   - **Issue:** The regex `(?i)(authorization\s*:\s*)(bearer\s+)?[A-Za-z0-9._\-+/=]{8,}` fails to redact `Authorization: Basic ...` headers because the space character (separating scheme and token) is not allowed in the token capture group.
   - **Fix:** Update the regex to support spaces or capture the remainder of the line. E.g., `r"(?i)(authorization\s*:\s*).+"`.

2. **Correctness: Renamed Files Excluded from Payload**
   - **Issue:** `git diff --numstat` outputs `old_path => new_path` for renames. The current parsing logic in `changed_file_stats` treats this entire string as the file path. This causes `is_excluded_path` and `build_compact_diff` to fail, resulting in renamed files being silently excluded from the payload.
   - **Fix:** Use `git diff --numstat -z` for reliable parsing or explicitly handle the `=>` format.

## Medium Severity

3. **Reliability: Silent Git Command Failures**
   - **Issue:** The `run_git` function swallows all non-zero exit codes and returns an empty string. If `git` fails (e.g., due to missing commit objects or binary issues), the script silently proceeds with partial or empty data.
   - **Fix:** Raise a `PayloadError` or similar exception when critical git commands fail.

4. **Correctness: Status Map Key Mismatch**
   - **Issue:** The `status_map` is built using the destination path from `--name-status`, while the file list uses the raw output from `--numstat`. For renamed files, the keys do not match (`new_path` vs `old => new`), causing status lookup failures.
   - **Fix:** Ensure consistent path parsing between the two git commands or use a single source of truth.

5. **Test Coverage: Missing Edge Cases**
   - **Issue:** The tests in `tests/agent/test_jules_payload.py` do not cover git failure scenarios or file renames, leaving critical logic unverified.
   - **Fix:** Add test cases for `run_git` failures and file rename handling.
