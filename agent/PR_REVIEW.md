# PR Review Findings

## Resolved Findings
All critical, high, medium, and low severity findings have been resolved.

- **Missing CSRF Protection:** Resolved by implementing Flask-WTF and enabling CSRF protection globally.
- **Tests Mask Security Vulnerability:** Resolved by enabling CSRF in tests and updating test clients.
- **Inappropriate Currency Type:** Resolved by switching from `float` to `decimal.Decimal`.
- **Unsafe Input Validation:** Resolved by strict type validation using `DecimalField`.
- **Deviation from Persistence Requirements:** Resolved by implementing `sqlite3` based in-memory repository.
- **Inconsistent Route Registration:** Resolved by registering blueprint at `/expenses` in tests.
