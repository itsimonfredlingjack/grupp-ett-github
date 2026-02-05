# Review Findings

## Security Regressions
1. **Missing CSRF Protection** (High)
   - The `add` route in `newsflash_app/presentation/routes.py` accepts POST requests without verifying a CSRF token. This allows Cross-Site Request Forgery attacks where a malicious site could trick a user into adding news flashes without their consent.
   - **Recommendation:** Integrate `Flask-WTF` for form handling which includes CSRF protection by default, or manually implement CSRF token verification.

2. **Unsafe HTTP Method for State Change** (Medium)
   - The `delete` route in `newsflash_app/presentation/routes.py` uses the GET method to delete items (`@bp.route("/delete/<int:item_id>", methods=["GET"])`). HTTP GET requests should be safe and idempotent. Using GET for deletion exposes the application to accidental data loss via web crawlers, browser prefetching, or simple link clicking/CSRF.
   - **Recommendation:** Change the route to accept only `POST` (or `DELETE`) requests and ensure it is protected by a CSRF token. Update the frontend to use a form for deletion instead of a link.

## Reliability and Edge Cases
3. **Data Consistency in Multi-Worker Environment** (Medium)
   - The `InMemoryNewsFlashRepository` is instantiated within `create_app`. If the application is deployed with multiple workers (e.g., using Gunicorn), each worker will maintain its own isolated copy of the data. This will lead to inconsistent application state where users see different data depending on which worker handles their request.
   - **Recommendation:** For the MVP, document that the application must be run with a single worker. For production, replace the in-memory repository with a database (e.g., SQLite, PostgreSQL) or a shared in-memory store like Redis.

4. **Race Condition in Item Limit Check** (Minor)
   - In `NewsFlashService.create_flash`, the application checks if the item count exceeds `MAX_ITEMS_PER_PAGE` before adding a new item. In a concurrent environment, multiple requests could pass this check simultaneously before any writes occur, causing the limit to be exceeded.
   - **Recommendation:** While low risk for this specific MVP, utilizing database constraints or atomic operations would prevent this race condition in a robust implementation.

5. **Documentation/Implementation Divergence** (Minor)
   - The `CURRENT_TASK.md` suggests "sqlite memory funkar för testerna", but the implementation uses a Python dictionary. While both are in-memory, SQLite would provide SQL semantics and easier migration to a real DB.
   - **Recommendation:** Clarify in the code or docs whether `dict` storage is intended as the final "InMemory" solution or a placeholder for SQLite-based in-memory storage.
