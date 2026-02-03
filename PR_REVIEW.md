# PR Review

## 1. Security Regressions

### Critical
- **Workflow Permissions**: `self_healing.yml` grants `contents: write`, `pull-requests: write`, and `issues: write` permissions. Granting `contents: write` to a workflow triggered by `workflow_run` (which can be triggered by a PR from a fork) is a major security risk. It should be restricted to `contents: read` and use `issues: write` for reporting remediation plans instead of committing directly.
- **Untrusted Code Checkout**: `self_healing.yml` checks out the `head_sha` from the `workflow_run` event. If the triggering workflow was from a fork, checking out this commit with write permissions (implied by the job permissions) allows for Remote Code Execution (RCE) if the checkout action or subsequent steps execute code from the repo.
- **Hardcoded Credentials**: `src/sejfa/core/admin_auth.py` contains hardcoded credentials (`admin`/`admin123`). This is unacceptable for any deployed environment.
- **Broken Authentication**: `AdminAuthService.validate_session_token` in `src/sejfa/core/admin_auth.py` only checks if the token starts with "token_", allowing trivial bypass (e.g., sending `Authorization: Bearer token_fake`).

### High
- **Unpinned Actions**: Workflows (`self_healing.yml`, `jules_review.yml`) use actions pinned by tag (e.g., `@v1.0.0`) instead of immutable SHA. Tags can be moved to malicious commits.
- **Hardcoded Secret Key**: `app.py` uses a hardcoded `secret_key` ("dev-secret-key"). It should be loaded from environment variables.

## 2. Reliability and Edge Cases

- **Infinite Loop Risk**: `self_healing.yml` does not check if the triggering actor is the Jules bot. If Jules commits a fix that fails CI, it will trigger itself recursively, consuming all Action minutes. Add `if: ... && github.actor != 'google-labs-jules[bot]'`.

## 3. Test Coverage Gaps

- **Auth Validation**: The weak token validation suggests a lack of negative test cases for invalid tokens that start with "token_". Tests should verify that tokens are cryptographically valid or at least match a stored session.

## 4. Performance Risks

- **Linear Search**: `SubscriberService.search_subscribers` iterates over all records (O(N)). This will degrade performance significantly as the subscriber base grows.
- **Full History Fetch**: Workflows use `fetch-depth: 0`, which downloads the entire git history. This will become a performance bottleneck. Use `fetch-depth: 1` unless history is explicitly required for analysis.
