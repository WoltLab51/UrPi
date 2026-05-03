import sqlite3
from .config import MEMORY_DB

def init_db():
    """Initialisiert die Memory-Datenbank."""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            type TEXT CHECK(type IN ('short_term', 'long_term', 'system')),
            timestamp TIMESTAMP,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()
