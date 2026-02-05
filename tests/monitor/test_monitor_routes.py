import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False  # Disable CSRF for testing
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_state(client):
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    data = response.get_json()
    assert "nodes" in data
    assert "task_info" in data

def test_update_state_valid(client):
    payload = {
        "node": "claude",
        "state": "active",
        "message": "Thinking..."
    }
    response = client.post("/api/monitor/state", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["current_state"]["current_node"] == "claude"

def test_update_state_invalid_node(client):
    payload = {
        "node": "invalid",
        "state": "active"
    }
    response = client.post("/api/monitor/state", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Invalid node" in data["error"]

def test_update_state_no_json(client):
    response = client.post("/api/monitor/state")
    assert response.status_code == 400

def test_reset_monitoring(client):
    # First set some state
    client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

    response = client.post("/api/monitor/reset")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["current_state"]["current_node"] is None

def test_update_task(client):
    payload = {
        "title": "New Task",
        "status": "running"
    }
    response = client.post("/api/monitor/task", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["current_state"]["task_info"]["title"] == "New Task"
    assert data["current_state"]["task_info"]["status"] == "running"
    # Verify start_time was automatically set
    assert data["current_state"]["task_info"]["start_time"] is not None

def test_update_task_no_json(client):
    response = client.post("/api/monitor/task")
    assert response.status_code == 400
