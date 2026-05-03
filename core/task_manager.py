import json
import os
import sqlite3
import uuid
from datetime import datetime
from .config import TASKS_DB

def _ensure_tasks_table():
    """Stellt sicher, dass die Tasks-Tabelle existiert."""
    os.makedirs(os.path.dirname(TASKS_DB), exist_ok=True)
    conn = sqlite3.connect(TASKS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
            status TEXT CHECK(status IN ('open', 'in_progress', 'done', 'failed')),
            assignee TEXT,
            acceptance_criteria TEXT,
            dependencies TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_task(task: dict):
    """Speichert einen Task in der Datenbank."""
    _ensure_tasks_table()
    conn = sqlite3.connect(TASKS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (id, title, description, priority, status, assignee, acceptance_criteria, dependencies, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.get("id", str(uuid.uuid4())),
        task["title"], task["description"], task.get("priority", "medium"),
        task.get("status", "open"), task.get("assignee"),
        json.dumps(task.get("acceptance_criteria", [])),
        json.dumps(task.get("dependencies", [])),
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
    columns = [col[0] for col in cursor.description]
    conn.close()
    if not task:
        return None
    return dict(zip(columns, task))
