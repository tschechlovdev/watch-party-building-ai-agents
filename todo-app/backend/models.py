import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")

VALID_STATUSES = ("todo", "in_progress", "done")


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
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                status     TEXT    NOT NULL DEFAULT 'todo'
            )
        """)
        columns = [r["name"] for r in conn.execute("PRAGMA table_info(todos)")]
        if "status" not in columns:
            conn.execute(
                "ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'"
            )
            conn.execute("UPDATE todos SET status = 'done' WHERE completed = 1")
        conn.commit()
