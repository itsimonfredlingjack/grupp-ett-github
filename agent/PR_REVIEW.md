# PR Review

## Security Regressions

### 1. CSRF Vulnerability in `GET /delete` (High)
The route `@bp.route("/delete/<int:item_id>", methods=["GET"])` performs a state-changing action (deletion) via a GET request. This is vulnerable to Cross-Site Request Forgery (CSRF), allowing attackers to trick users into deleting items by clicking a link or visiting a malicious page.
**Recommendation**: Change the route to use `POST` (or `DELETE` with JS) and ensure the delete action in `index.html` uses a `<form method="POST">` containing a CSRF token.

### 2. Missing CSRF Protection on Forms (High)
The `POST /add` form in `index.html` and the corresponding route in `routes.py` lack CSRF protection mechanisms (e.g., a hidden token). This allows attackers to forge requests to add malicious news flashes.
**Recommendation**: Integrate `Flask-WTF` to handle forms or manually implement CSRF token generation and validation.

### 3. Missing `SECRET_KEY` Configuration (Medium)
The application factory `create_app` in `newsflash_app/flask_app.py` does not configure `SECRET_KEY`. While sessions are not currently used explicitly, this key is required for signing session cookies and generating secure tokens (like CSRF tokens).
**Recommendation**: Configure `app.config['SECRET_KEY']` using an environment variable, falling back to a secure random string or raising an error if missing in production.

## Reliability and Edge Cases

### 4. Data Persistence (Info)
The application currently uses `InMemoryNewsFlashRepository`, meaning all data is lost when the application restarts. This limits the application's utility to a single session or testing environment.
**Recommendation**: Verify if this meets the long-term requirements. For production, migrate to a persistent storage solution (e.g., SQLite, PostgreSQL).

## Test Coverage Gaps

### 5. Excellent Coverage (Info)
The integration tests in `tests/integration_newsflash/test_newsflash_flask.py` provide excellent coverage of the defined business rules (headline length, category validation, item limits) and success/error paths.

## Correctness

### 6. Architecture Compliance (Info)
The implementation correctly follows the specified Clean Architecture/3-layer separation. The business logic (`NewsFlashService`) is decoupled from Flask and HTTP concerns, and the data layer is abstracted via a repository protocol.
