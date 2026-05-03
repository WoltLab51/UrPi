import sqlite3
import uuid
from datetime import datetime
from .config import TASKS_DB

def save_task(task: dict):
    """Speichert einen Task in der Datenbank."""
    conn = sqlite3.connect(TASKS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (id, title, description, priority, status, assignee, acceptance_criteria, dependencies, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.get("id", str(uuid.uuid4())),
        task["title"], task["description"], task.get("priority", "medium"),
        task.get("status", "open"), task.get("assignee"),
        str(task.get("acceptance_criteria", [])), str(task.get("dependencies", [])),
        task.get("created_at", datetime.utcnow().isoformat()),
        task.get("updated_at", datetime.utcnow().isoformat())
    ))
    conn.commit()
    conn.close()

def get_task(task_id: str) -> dict:
    """Lädt einen Task aus der Datenbank."""
    conn = sqlite3.connect(TASKS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if not task:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, task))
