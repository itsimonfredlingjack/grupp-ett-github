import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_state(client):
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    assert "nodes" in response.json


def test_update_state_success(client):
    data = {"node": "jules", "state": "active", "message": "Testing"}
    response = client.post("/api/monitor/state", json=data)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["current_state"]["nodes"]["jules"]["active"] is True


def test_update_state_invalid_node(client):
    data = {"node": "invalid", "state": "active", "message": "Testing"}
    response = client.post("/api/monitor/state", json=data)
    assert response.status_code == 400
    assert response.json["success"] is False


def test_update_state_no_data(client):
    # Testing with explicit None to simulate no data
    response = client.post("/api/monitor/state", json=None)
    assert response.status_code == 400


def test_reset_monitoring(client):
    # First set some state
    client.post(
        "/api/monitor/state",
        json={"node": "jules", "state": "active", "message": "t"},
    )

    response = client.post("/api/monitor/reset")
    assert response.status_code == 200
    assert response.json["success"] is True

    # Verify state is reset
    state = client.get("/api/monitor/state").json
    assert state["nodes"]["jules"]["active"] is False


def test_update_task(client):
    data = {"title": "New Task", "status": "running"}
    response = client.post("/api/monitor/task", json=data)
    assert response.status_code == 200
    assert response.json["success"] is True

    state = client.get("/api/monitor/state").json
    assert state["task_info"]["title"] == "New Task"
    assert state["task_info"]["status"] == "running"
