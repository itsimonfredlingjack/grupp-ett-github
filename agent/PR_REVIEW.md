## High Severity

### 1. Decouple test setup from API endpoints (Reliability)
The test `test_get_list_with_flashes` uses `client.post` to set up state. This couples the `GET` test to the `POST` implementation. If `POST` fails, the `GET` test will fail misleadingly.
**Action:** Seed the `InMemoryNewsFlashRepository` directly in the test or fixture. Update the `app` fixture to expose the repository instance (e.g., return `(app, repository)`).

## Medium Severity

### 2. Divergence from Application Factory (Correctness)
The `app` fixture manually constructs the Flask app and registers the blueprint. This bypasses the standard `create_app` factory in `app.py`, potentially missing global configurations, error handlers, or security headers present in the main application.
**Action:** Use `create_app` from `app.py` if possible, or ensure the test app configuration mirrors production.

## Low Severity

### 3. Use raw strings for Unicode (Readability)
The tests use Unicode escape sequences (e.g., `\u00e4`) for Swedish characters. Python 3 source files are UTF-8 by default.
**Action:** Use literal characters (e.g., `"Titel krävs"`) for better readability.

### 4. Hardcoded error strings (Maintainability)
The tests assert exact Swedish error messages (e.g., "Titel krävs"). This makes tests brittle to copy changes.
**Action:** Verify error codes or structured error keys if available, or define expected messages in a shared constant.
