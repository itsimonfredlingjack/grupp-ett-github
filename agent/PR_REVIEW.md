# PR Review Findings

## Security Regressions

1. **Public Write Access (High)**
   The endpoints `POST /cursorflash/add` and `PUT /cursorflash/update/<id>` are publicly accessible without authentication. Since `AdminAuthService` exists and protects other admin routes, these should likely be protected as well.
   *File: `src/sejfa/cursorflash/routes.py`*

## Reliability and Edge Cases

2. **Data Persistence (Medium)**
   The implementation uses `InMemoryNewsFlashRepository`, meaning all data will be lost on application restart. While acceptable for testing, this is a risk for production use if not intended as a temporary MVP state.
   *File: `src/sejfa/cursorflash/repository.py`*

3. **Hardcoded Error Strings (Low)**
   Swedish error messages (e.g., "Titel krävs") are hardcoded in `service.py`, `routes.py`, and `test_routes.py`. This makes maintenance difficult and tests brittle. Use constants or a translation layer.
   *File: `src/sejfa/cursorflash/service.py`*

## Correctness

4. **Missing DELETE Endpoint (Low)**
   `NewsFlashService` implements `delete_flash`, but `routes.py` does not expose a corresponding DELETE endpoint. Verify if this feature is missing or intentionally omitted.
   *File: `src/sejfa/cursorflash/routes.py`*

5. **Input Validation Consistency (Low)**
   Input handling in `routes.py` is inconsistent: `title` defaults to empty string, while `content` checks for `None`. Standardize input retrieval and validation flow.
   *File: `src/sejfa/cursorflash/routes.py`*

## Test Coverage Gaps

6. **Implicit Test State (Low)**
   `test_get_list_with_flashes` relies on `client.post` to set up state, coupling the GET test to POST logic. Seed the repository directly in the test setup for better isolation.
   *File: `tests/cursorflash/test_routes.py`*
