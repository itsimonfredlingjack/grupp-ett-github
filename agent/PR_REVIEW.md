# PR Review Findings

## Security Risks
1. **High - Unsafe HTTP Method for State Change**: The route `GET /delete/<int:item_id>` performs a destructive action (deletion) via GET request. This is vulnerable to CSRF attacks and accidental deletion by web crawlers.
   - **Recommendation**: Change the route to `POST /delete/<int:item_id>` and update the HTML form/button to submit a POST request (e.g., using a mini-form).

2. **High - Missing CSRF Protection**: The `POST /add` endpoint lacks Cross-Site Request Forgery (CSRF) protection. Malicious sites could submit forms on behalf of authenticated users (though auth is not implemented yet, it's a security best practice gap).
   - **Recommendation**: Integrate `Flask-WTF` or `flask-wtf.csrf` and include CSRF tokens in forms.

## Reliability & Best Practices
3. **Medium - Hardcoded IDs in Tests**: `test_delete_flash_item` relies on the assumption that the first created item has ID `1`. This is brittle and may break if ID generation strategy changes (e.g., UUIDs).
   - **Recommendation**: Retrieve the ID dynamically from the created item or parse it from the response/redirect if possible, or verify the deletion by content rather than ID assumption.

4. **Low - Idempotency Validation**: `test_delete_nonexistent_item_doesnt_crash` asserts success (200 OK via redirect) when deleting a non-existent item. While safe, it might mask errors.
   - **Recommendation**: Consider adding a flash message or specific return code if the item was not found, to improve user feedback.

## Test Coverage
5. **Low - Edge Case Coverage**: Tests cover basic happy paths and length validation, but edge cases like very long strings, special characters in headlines, or rapid repeated submissions (rate limiting) are not covered.
   - **Recommendation**: Add test cases for maximum length boundaries and special characters.
