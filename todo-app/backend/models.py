import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        # Add status column if it doesn't exist yet (safe on both fresh and existing DBs)
        try:
            conn.execute(
                "ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'"
            )
        except Exception:
            pass  # Column already exists — ignore
        conn.commit()
