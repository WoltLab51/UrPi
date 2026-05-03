import os
from pathlib import Path

# Basisverzeichnis
BASE_DIR = Path(__file__).parent.parent

# Datenbankpfade
TASKS_DB = os.path.join(BASE_DIR, "data", "tasks.db")
MEMORY_DB = os.path.join(BASE_DIR, "data", "memory.db")
MODULES_DB = os.path.join(BASE_DIR, "data", "modules.db")

# Standard-Agenten
DEFAULT_AGENTS = [
    {"name": "Mistral Vibe", "role": "coding", "capabilities": ["code_generation", "testing"]},
    {"name": "Devstral 2", "role": "automation", "capabilities": ["task_execution", "validation"]},
]
