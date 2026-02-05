# PR Review Findings

## Security Regressions

1. **Critical: Unauthenticated Write Access**
   The endpoints `POST /cursorflash/add` and `PUT /cursorflash/update/<id>` are exposed without any authentication. This allows unprivileged users to modify data.
   *File*: `src/sejfa/cursorflash/routes.py`

2. **High: Missing CSRF Protection**
   The state-changing endpoints accept JSON payloads but lack CSRF validation, making them vulnerable if accessed via a browser session.
   *File*: `src/sejfa/cursorflash/routes.py`

## Reliability and Edge Cases

3. **High: Data Persistence Risk**
   The application uses `InMemoryNewsFlashRepository`, leading to data loss on application restart. This is critical if the feature is intended for production.
   *File*: `src/sejfa/cursorflash/repository.py`

4. **Medium: Hardcoded Language/Strings**
   Error messages and API keys (e.g., `fel`) are hardcoded in Swedish. This violates separation of concerns and hinders internationalization.
   *File*: `src/sejfa/cursorflash/service.py`

## Correctness

5. **Low: Inconsistent Input Validation**
   Title defaults to empty string while content defaults to `None` before validation. This inconsistency can lead to subtle bugs.
   *File*: `src/sejfa/cursorflash/routes.py`

## Test Coverage Gaps

6. **Low: Coupled Test Setup**
   Tests like `test_get_list_with_flashes` use the API (`client.post`) to set up state. Prefer seeding the repository directly (`repository.add()`) to decouple tests.
   *File*: `tests/cursorflash/test_routes.py`
