# Code Review Findings

**Note:** These findings are based on the visible portion of the provided diff. Some issues (e.g., missing tests) might be addressed in the truncated sections of the file.

## Medium Severity

### 1. Test Setup Coupling (Reliability)
**File:** `tests/cursorflash/test_routes.py` (Line 49)
**Description:** `test_get_list_with_flashes` uses `client.post` to seed data. This couples the test for the GET endpoint to the implementation of the POST endpoint. If POST fails, the GET test will fail, which can be confusing.
**Actionable:** Seed the repository directly (e.g., using `repository.save()`) in the test or a fixture to decouple the test setup from the API implementation.

### 2. Unverified Test Setup (Correctness)
**File:** `tests/cursorflash/test_routes.py` (Line 49)
**Description:** In `test_get_list_with_flashes`, the setup step `client.post(...)` is performed without asserting its success. If the setup fails (e.g., returns 500), the subsequent assertion `len(data["flashes"]) == 1` will fail with a misleading error.
**Actionable:** Add an assertion (e.g., `assert response.status_code == 201`) immediately after the setup step to ensure the test environment is correctly prepared.

### 3. Missing Content Validation Tests (Test Coverage Gaps)
**File:** `tests/cursorflash/test_routes.py`
**Description:** The commit message mentions validation rules for content length (10-5000 chars), but the visible tests only cover title validation. If not present in the truncated code, this is a coverage gap.
**Actionable:** Verify if tests for content length boundaries exist; if not, add them.

### 4. Missing Tests for Update Endpoint (Test Coverage Gaps)
**File:** `tests/cursorflash/test_routes.py`
**Description:** The commit message mentions implementing `PUT /update/<id>`, but there are no visible tests for this endpoint. If not present in the truncated code, this is a coverage gap.
**Actionable:** Verify if tests for `PUT /update/<id>` exist; if not, add them.

## Minor Severity

### 5. Brittle Error Message Assertions (Reliability)
**File:** `tests/cursorflash/test_routes.py` (Line 100)
**Description:** Asserting exact error strings like "Titel krävs" makes tests brittle to changes in wording or localization.
**Actionable:** Verify error codes or structured error keys if available, or define error messages as constants in the source code and use them in tests.
