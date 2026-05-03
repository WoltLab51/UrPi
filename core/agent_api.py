from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import json
import sqlite3
import os
import uuid
from datetime import datetime, timezone
from .config import TASKS_DB, MEMORY_DB, MODULES_DB, DEFAULT_AGENTS

# --- Datenbank-Initialisierung ---
def init_db():
    try:
        os.makedirs(os.path.dirname(TASKS_DB), exist_ok=True)
        for db_path in [TASKS_DB, MEMORY_DB, MODULES_DB]:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if "tasks" in str(db_path):
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
            elif "memory" in str(db_path):
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        type TEXT CHECK(type IN ('short_term', 'long_term', 'system')),
                        timestamp TIMESTAMP,
                        metadata TEXT
                    )
                """)
            elif "modules" in str(db_path):
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS modules (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        description TEXT,
                        capabilities TEXT,
                        api_endpoint TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        registered_at TIMESTAMP
                    )
                """)
            conn.commit()
            conn.close()
    except Exception as e:
        raise RuntimeError(f"Datenbank-Initialisierung fehlgeschlagen: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Ur-PiGenus v0.1 API",
    description="Orchestrator für GENUS: Tasks, Memory, Module.",
    version="0.1.0",
    lifespan=lifespan
)

# --- Hilfsfunktionen ---
def _parse_task(row: dict) -> dict:
    """Parse JSON fields from a task row."""
    for field in ("acceptance_criteria", "dependencies"):
        if isinstance(row.get(field), str):
            try:
                row[field] = json.loads(row[field])
            except (json.JSONDecodeError, TypeError):
                row[field] = []
    return row

def _parse_memory_entry(row: dict) -> dict:
    """Parse JSON fields from a memory row."""
    if isinstance(row.get("metadata"), str):
        try:
            row["metadata"] = json.loads(row["metadata"])
        except (json.JSONDecodeError, TypeError):
            row["metadata"] = {}
    return row


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    assignee: Optional[str] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[Literal["open", "in_progress", "done", "failed"]] = None
    assignee: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None

class Task(TaskCreate):
    id: str
    status: str = "open"
    created_at: str
    updated_at: str

class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    type: str = "long_term"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Agent(BaseModel):
    name: str
    role: str
    capabilities: List[str]

class AgentRegisterResponse(BaseModel):
    status: str
    agent: Agent

class HealthResponse(BaseModel):
    status: str
    version: str
    workers: int

class RootResponse(BaseModel):
    name: str
    version: str
    docs: str
    health: str

# --- Task-Endpunkte ---
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    try:
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        columns = [col[0] for col in cursor.description]
        tasks = [_parse_task(dict(zip(columns, row))) for row in cursor.fetchall()]
        conn.close()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {e}")

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    try:
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        task_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO tasks (id, title, description, priority, status, assignee, acceptance_criteria, dependencies, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, task.title, task.description, task.priority, "open",
            task.assignee, json.dumps(task.acceptance_criteria), json.dumps(task.dependencies), now, now
        ))
        conn.commit()
        conn.close()
        return Task(
            id=task_id, title=task.title, description=task.description,
            priority=task.priority, status="open", assignee=task.assignee,
            acceptance_criteria=task.acceptance_criteria, dependencies=task.dependencies,
            created_at=now, updated_at=now
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task konnte nicht erstellt werden: {e}")

@app.get("/tasks/next", response_model=Optional[Task])
def get_next_task():
    try:
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks WHERE status = 'open'
            ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END,
                     created_at ASC
            LIMIT 1
        """)
        columns = [col[0] for col in cursor.description]
        task = cursor.fetchone()
        conn.close()
        return _parse_task(dict(zip(columns, task))) if task else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {e}")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskUpdate):
    try:
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        current_task = cursor.fetchone()
        if not current_task:
            conn.close()
            raise HTTPException(status_code=404, detail="Task not found")
        columns = [col[0] for col in cursor.description]
        current_task_dict = _parse_task(dict(zip(columns, current_task)))
        updates = task_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_task = {**current_task_dict, **updates}
        updated_task["updated_at"] = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, status = ?, assignee = ?, acceptance_criteria = ?, dependencies = ?, updated_at = ?
            WHERE id = ?
        """, (
            updated_task["title"], updated_task["description"], updated_task["priority"],
            updated_task["status"], updated_task["assignee"],
            json.dumps(updated_task["acceptance_criteria"]),
            json.dumps(updated_task["dependencies"]),
            updated_task["updated_at"], task_id
        ))
        conn.commit()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        result = _parse_task(dict(zip(columns, cursor.fetchone())))
        conn.close()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task konnte nicht aktualisiert werden: {e}")

# --- Memory-Endpunkte ---
@app.get("/memory", response_model=List[MemoryEntry])
def get_memory():
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory")
        columns = [col[0] for col in cursor.description]
        entries = [_parse_memory_entry(dict(zip(columns, row))) for row in cursor.fetchall()]
        conn.close()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {e}")

@app.post("/memory", response_model=MemoryEntry, status_code=status.HTTP_201_CREATED)
def add_memory(entry: MemoryEntry):
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO memory (id, content, type, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (entry.id, entry.content, entry.type, now, json.dumps(entry.metadata)))
        conn.commit()
        conn.close()
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory-Eintrag konnte nicht gespeichert werden: {e}")

# --- Module- und Agenten-Endpunkte ---
@app.get("/modules", response_model=List[Dict])
def get_modules():
    try:
        conn = sqlite3.connect(MODULES_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM modules")
        columns = [col[0] for col in cursor.description]
        modules = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {e}")

@app.post("/modules/register", response_model=Dict, status_code=status.HTTP_201_CREATED)
def register_module(module: Dict):
    try:
        conn = sqlite3.connect(MODULES_DB)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        module_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO modules (id, name, version, description, capabilities, api_endpoint, is_active, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            module_id, module["name"], module["version"], module.get("description", ""),
            str(module.get("capabilities", [])), module["api_endpoint"], module.get("is_active", True), now
        ))
        conn.commit()
        conn.close()
        return {"status": "registered", "module_id": module_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modul konnte nicht registriert werden: {e}")

@app.get("/agents", response_model=List[Agent])
def get_agents():
    return DEFAULT_AGENTS

@app.post("/agents/register", response_model=AgentRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent: Agent):
    DEFAULT_AGENTS.append(agent.model_dump())
    return AgentRegisterResponse(status="registered", agent=agent)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version="0.1.0", workers=1)

@app.get("/", response_model=RootResponse)
def root():
    return RootResponse(
        name="Ur-PiGenus",
        version="0.1.0",
        docs="/docs",
        health="/health"
    )
