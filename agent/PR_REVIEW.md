# PR Review Findings

## High Severity

### 1. Duplicate Integration Tests (Maintenance)
The existing `tests/test_news_flash.py` and the new `tests/newsflash/test_integration.py` cover overlapping functionality (integration tests for newsflash routes).
**Action:** Consolidate integration tests into `tests/newsflash/test_integration.py` and remove `tests/test_news_flash.py`.

### 2. Incomplete Legacy Cleanup (Maintenance)
The PR adds tests for `SubscriptionService` in `tests/newsflash/` but the previous implementation was in `cursorflash`.
**Action:** Verify removal of `tests/cursorflash/test_business.py` and `src/sejfa/cursorflash/business/subscription_service.py` to prevent dead code and incorrect test targeting.

### 3. Permissive Email Regex (Security)
The email validation regex `...@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` allows consecutive dots (`..`) and leading/trailing special characters in the domain part.
**Action:** Use a stricter regex or `email-validator` library to prevent invalid domains.

## Medium Severity

### 4. Code Duplication in Test Fixtures (Refactoring)
`tests/test_app.py` defines a `client` fixture locally, which cannot be shared with new tests.
**Action:** Create `tests/conftest.py` and move the `client` fixture there to enable reuse across all test modules.

## Low Severity

### 5. Missing Package Initialization (Best Practice)
The new `tests/newsflash` directory lacks an `__init__.py` file.
**Action:** Add `tests/newsflash/__init__.py` to ensure consistent package behavior.

### 6. Weak Date Validation (Correctness)
The test `test_process_subscription_with_valid_data` checks for the existence of `subscribed_at` but not its format.
**Action:** Add an assertion to verify `subscribed_at` is a valid ISO-8601 string.
