# PR Review Findings

## Security Regressions

1. **Critical**: Hardcoded `secret_key` in `app.py`.
   - **Location**: `app.py:24`
   - **Issue**: `app.secret_key = "dev-secret-key"` is hardcoded.
   - **Risk**: Allows attackers to sign session cookies and impersonate users if the key is leaked or guessed.

2. **Critical**: Hardcoded Admin Credentials in `src/sejfa/core/admin_auth.py`.
   - **Location**: `src/sejfa/core/admin_auth.py:18`
   - **Issue**: `VALID_ADMIN` dictionary contains hardcoded username and password.
   - **Risk**: Anyone with source access can authenticate as admin.

3. **High**: Insecure Session Token Validation in `src/sejfa/core/admin_auth.py`.
   - **Location**: `src/sejfa/core/admin_auth.py:60`
   - **Issue**: `token.startswith("token_")` accepts any token with that prefix.
   - **Risk**: Allows authentication bypass by providing any string starting with `token_`.

4. **Medium**: Weak Session Token Generation in `src/sejfa/core/admin_auth.py`.
   - **Location**: `src/sejfa/core/admin_auth.py:47`
   - **Issue**: Use of `hash()` which is not cryptographically secure and varies by session/seed.
   - **Risk**: Predictable session tokens.

## Reliability and Edge Cases

5. **Medium**: In-Memory Subscriber Storage in `src/sejfa/core/subscriber_service.py`.
   - **Location**: `src/sejfa/core/subscriber_service.py:22`
   - **Issue**: `_subscribers` is a simple dictionary.
   - **Risk**: All subscriber data is lost when the application restarts.
