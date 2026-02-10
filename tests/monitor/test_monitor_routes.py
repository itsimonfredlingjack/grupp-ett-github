import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client


def test_update_state_valid_json(client):
    response = client.post(
        "/api/monitor/state",
        json={"node": "jules", "state": "active", "message": "Test message"},
    )
    assert response.status_code == 200
    assert response.json["success"] is True


def test_update_state_missing_node(client):
    response = client.post(
        "/api/monitor/state", json={"state": "active", "message": "Test message"}
    )
    assert response.status_code == 400
    assert b"Invalid node" in response.data


def test_update_state_missing_status(client):
    response = client.post(
        "/api/monitor/state", json={"node": "jules", "message": "Test message"}
    )
    assert response.status_code == 200
    assert response.json["success"] is True


def test_get_state_returns_json(client):
    client.post(
        "/api/monitor/state",
        json={"node": "jules", "state": "active", "message": "Test message"},
    )

    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    data = response.json
    assert "nodes" in data
    assert "jules" in data["nodes"]
    assert data["nodes"]["jules"]["active"] is True


def test_update_state_invalid_content_type(client):
    response = client.post(
        "/api/monitor/state",
        data="not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in [400, 500]
