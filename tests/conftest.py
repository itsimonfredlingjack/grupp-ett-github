import pytest


@pytest.fixture(autouse=True)
def _test_auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin123")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
