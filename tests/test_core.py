import pytest
import os
from fastapi.testclient import TestClient
import core.agent_api as api_module
from core.agent_api import app, init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("testdata")
    original = (api_module.TASKS_DB, api_module.MEMORY_DB, api_module.MODULES_DB)
    api_module.TASKS_DB = str(tmp / "tasks.db")
    api_module.MEMORY_DB = str(tmp / "memory.db")
    api_module.MODULES_DB = str(tmp / "modules.db")
    init_db()
    yield
    api_module.TASKS_DB, api_module.MEMORY_DB, api_module.MODULES_DB = original

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["workers"] == 1

def test_create_task():
    task_data = {"title": "Test Task", "description": "Ein Test-Task.", "priority": "high"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    task = response.json()
    assert "id" in task
    assert task["title"] == task_data["title"]
    assert task["status"] == "open"

def test_get_tasks():
    task_data = {"title": "Test Task 2", "description": "Ein weiterer Test-Task.", "priority": "medium"}
    client.post("/tasks", json=task_data)
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1

def test_update_task():
    task_data = {"title": "Task zum Aktualisieren", "description": "Wird gleich aktualisiert.", "priority": "low"}
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]
    update_data = {"status": "in_progress", "priority": "high"}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == "in_progress"
    assert updated_task["priority"] == "high"

def test_get_next_task():
    task_data = {"title": "Nächster Task", "description": "Sollte als nächstes zurückgegeben werden.", "priority": "high"}
    client.post("/tasks", json=task_data)
    response = client.get("/tasks/next")
    assert response.status_code == 200
    task = response.json()
    assert task is not None
    assert task["priority"] == "high"

def test_error_handling():
    response = client.put("/tasks/non-existent-id", json={"status": "done"})
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

def test_get_memory():
    """Test GET /memory returns 200 OK and a list."""
    response = client.get("/memory")
    assert response.status_code == 200
    memory_entries = response.json()
    assert isinstance(memory_entries, list)

def test_create_memory():
    """Test POST /memory creates a memory entry with auto-generated ID."""
    memory_data = {
        "content": "Deploy-Test",
        "type": "system",
        "metadata": {"source": "pi5_check"}
    }
    response = client.post("/memory", json=memory_data)
    assert response.status_code == 201
    memory_entry = response.json()
    assert "id" in memory_entry
    assert len(memory_entry["id"]) > 0  # UUID should be generated
    assert memory_entry["content"] == memory_data["content"]
    assert memory_entry["type"] == memory_data["type"]
    assert memory_entry["metadata"] == memory_data["metadata"]

def test_memory_persistence():
    """Test that GET /memory contains the entry created by POST /memory."""
    # Create a memory entry
    memory_data = {
        "content": "Persistence test entry",
        "type": "long_term",
        "metadata": {"test": "persistence"}
    }
    create_response = client.post("/memory", json=memory_data)
    assert create_response.status_code == 201
    created_entry = create_response.json()
    created_id = created_entry["id"]

    # Verify it appears in GET /memory
    get_response = client.get("/memory")
    assert get_response.status_code == 200
    memory_entries = get_response.json()

    # Find the created entry in the list
    found = False
    for entry in memory_entries:
        if entry["id"] == created_id:
            found = True
            assert entry["content"] == memory_data["content"]
            assert entry["type"] == memory_data["type"]
            assert entry["metadata"] == memory_data["metadata"]
            break

    assert found, f"Created memory entry with id {created_id} not found in GET /memory response"
