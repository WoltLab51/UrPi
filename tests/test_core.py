import pytest
from fastapi.testclient import TestClient
from core.agent_api import app
import sqlite3
import os

client = TestClient(app)

TEST_TASKS_DB = "test_tasks.db"
TEST_MEMORY_DB = "test_memory.db"
TEST_MODULES_DB = "test_modules.db"

@pytest.fixture(scope="module")
def setup_test_db():
    for db_path in [TEST_TASKS_DB, TEST_MEMORY_DB, TEST_MODULES_DB]:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if "tasks" in db_path:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT,
                    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
                    status TEXT CHECK(status IN ('open', 'in_progress', 'done', 'failed')),
                    assignee TEXT, acceptance_criteria TEXT, dependencies TEXT,
                    created_at TIMESTAMP, updated_at TIMESTAMP
                )
            """)
        elif "memory" in db_path:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id TEXT PRIMARY KEY, content TEXT NOT NULL,
                    type TEXT CHECK(type IN ('short_term', 'long_term', 'system')),
                    timestamp TIMESTAMP, metadata TEXT
                )
            """)
        elif "modules" in db_path:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS modules (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL,
                    description TEXT, capabilities TEXT, api_endpoint TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1, registered_at TIMESTAMP
                )
            """)
        conn.commit()
        conn.close()
    yield
    for db in [TEST_TASKS_DB, TEST_MEMORY_DB, TEST_MODULES_DB]:
        if os.path.exists(db):
            os.remove(db)

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
    task_data = {"title": "Nächster Task", "description": "Sollte als nächstes zurückgegeben werden.", "priority": "high", "status": "open"}
    client.post("/tasks", json=task_data)
    response = client.get("/tasks/next")
    assert response.status_code == 200
    task = response.json()
    assert task is not None
    assert task["title"] == task_data["title"]

def test_error_handling():
    response = client.put("/tasks/non-existent-id", json={"status": "done"})
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]
