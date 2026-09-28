import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


VALID_STATUSES = ("todo", "in_progress", "done")


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                status     TEXT    NOT NULL DEFAULT 'todo',
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        # Add status column to pre-existing databases that lack it.
        # SQLite fills existing rows with the DEFAULT value ('todo'), so we must
        # fix rows where completed=1 but status was blindly set to 'todo' by ALTER TABLE.
        try:
            conn.execute("ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'")
        except Exception:
            pass  # Column already exists
        # Backfill: any completed row whose status is still 'todo' predates this migration
        conn.execute(
            "UPDATE todos SET status = 'done' WHERE completed = 1 AND status = 'todo'"
        )
        conn.commit()
