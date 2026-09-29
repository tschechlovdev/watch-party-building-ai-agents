import pytest
import os
import tempfile
from app import app
import models


@pytest.fixture
def client(tmp_path):
    """Create a test client with an isolated temporary database."""
    db_file = tmp_path / "test_todos.db"
    models.DB_PATH = str(db_file)
    models.init_db()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# GET /api/todos
# ---------------------------------------------------------------------------

class TestGetTodos:
    def test_returns_empty_list_initially(self, client):
        resp = client.get("/api/todos")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_all_todos_newest_first(self, client):
        client.post("/api/todos", json={"title": "First"})
        client.post("/api/todos", json={"title": "Second"})

        resp = client.get("/api/todos")
        data = resp.get_json()
        assert len(data) == 2
        assert data[0]["title"] == "Second"
        assert data[1]["title"] == "First"


# ---------------------------------------------------------------------------
# POST /api/todos
# ---------------------------------------------------------------------------

class TestCreateTodo:
    def test_creates_todo_and_returns_201(self, client):
        resp = client.post("/api/todos", json={"title": "Buy milk"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["title"] == "Buy milk"
        assert body["completed"] is False
        assert "id" in body
        assert "created_at" in body

    def test_strips_whitespace_from_title(self, client):
        resp = client.post("/api/todos", json={"title": "  Trimmed  "})
        assert resp.status_code == 201
        assert resp.get_json()["title"] == "Trimmed"

    def test_rejects_empty_title(self, client):
        resp = client.post("/api/todos", json={"title": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_rejects_whitespace_only_title(self, client):
        resp = client.post("/api/todos", json={"title": "   "})
        assert resp.status_code == 400

    def test_rejects_missing_title(self, client):
        resp = client.post("/api/todos", json={})
        assert resp.status_code == 400

    def test_rejects_non_json_body(self, client):
        resp = client.post("/api/todos", data="not json",
                           content_type="text/plain")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PUT /api/todos/<id>
# ---------------------------------------------------------------------------

class TestUpdateTodo:
    def _create(self, client, title="Original"):
        return client.post("/api/todos", json={"title": title}).get_json()

    def test_updates_title(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Updated"

    def test_toggles_completed(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": True})
        assert resp.status_code == 200
        assert resp.get_json()["completed"] is True

    def test_updates_title_and_completed_together(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}",
                          json={"title": "New", "completed": True})
        body = resp.get_json()
        assert body["title"] == "New"
        assert body["completed"] is True

    def test_returns_404_for_nonexistent_id(self, client):
        resp = client.put("/api/todos/999", json={"title": "x"})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_rejects_empty_title_on_update(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"title": "  "})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/todos/<id>
# ---------------------------------------------------------------------------

class TestDeleteTodo:
    def test_deletes_todo_and_returns_204(self, client):
        todo = client.post("/api/todos", json={"title": "To delete"}).get_json()
        resp = client.delete(f"/api/todos/{todo['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_deleted_todo_no_longer_in_list(self, client):
        todo = client.post("/api/todos", json={"title": "Gone"}).get_json()
        client.delete(f"/api/todos/{todo['id']}")
        ids = [t["id"] for t in client.get("/api/todos").get_json()]
        assert todo["id"] not in ids

    def test_returns_404_for_nonexistent_id(self, client):
        resp = client.delete("/api/todos/999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# Generic 404
# ---------------------------------------------------------------------------

class TestNotFound:
    def test_unknown_route_returns_json_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}


# ---------------------------------------------------------------------------
# Status field — GET response includes status
# ---------------------------------------------------------------------------

class TestStatusField:
    def test_new_todo_has_default_status_todo(self, client):
        resp = client.post("/api/todos", json={"title": "Task"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "todo"
        assert body["completed"] is False

    def test_get_returns_status_field(self, client):
        client.post("/api/todos", json={"title": "Task"})
        items = client.get("/api/todos").get_json()
        assert "status" in items[0]

    def test_create_with_explicit_status_in_progress(self, client):
        resp = client.post("/api/todos", json={"title": "WIP", "status": "in_progress"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_create_with_status_done_sets_completed_true(self, client):
        resp = client.post("/api/todos", json={"title": "Done task", "status": "done"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "done"
        assert body["completed"] is True

    def test_create_with_invalid_status_returns_400(self, client):
        resp = client.post("/api/todos", json={"title": "Bad", "status": "urgent"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# Status sync — PUT /api/todos/<id>
# ---------------------------------------------------------------------------

class TestStatusSync:
    def _create(self, client, title="Task", status="todo"):
        return client.post("/api/todos", json={"title": title, "status": status}).get_json()

    def test_update_status_to_done_sets_completed_true(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "done"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "done"
        assert body["completed"] is True

    def test_update_status_to_in_progress_sets_completed_false(self, client):
        todo = self._create(client, status="done")
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "in_progress"})
        body = resp.get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_update_status_to_todo_sets_completed_false(self, client):
        todo = self._create(client, status="done")
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "todo"})
        body = resp.get_json()
        assert body["status"] == "todo"
        assert body["completed"] is False

    def test_update_completed_true_sets_status_done(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": True})
        body = resp.get_json()
        assert body["completed"] is True
        assert body["status"] == "done"

    def test_update_completed_false_from_done_sets_status_todo(self, client):
        todo = self._create(client, status="done")
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": False})
        body = resp.get_json()
        assert body["completed"] is False
        assert body["status"] == "todo"

    def test_update_completed_false_preserves_in_progress(self, client):
        """Un-completing an in_progress todo should keep status in_progress."""
        todo = self._create(client, status="in_progress")
        # Force completed=1 on an in_progress todo via direct status=done then back
        client.put(f"/api/todos/{todo['id']}", json={"status": "done"})
        client.put(f"/api/todos/{todo['id']}", json={"status": "in_progress"})
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": False})
        body = resp.get_json()
        assert body["completed"] is False
        assert body["status"] == "in_progress"

    def test_update_invalid_status_returns_400(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "critical"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_status_takes_precedence_when_both_provided(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "in_progress", "completed": True})
        body = resp.get_json()
        # status wins → in_progress → completed=False
        assert body["status"] == "in_progress"
        assert body["completed"] is False


# ---------------------------------------------------------------------------
# Migration backfill — rows inserted before status column existed
# ---------------------------------------------------------------------------

class TestMigrationBackfill:
    def test_pre_migration_rows_are_backfilled_on_init_db(self, tmp_path):
        """Simulate a DB that existed before the status column was added.

        Steps:
        1. Create a DB with the old schema (no status column).
        2. Insert a row directly.
        3. Run init_db() to simulate the server restarting with the new code.
        4. Verify the row now has status='todo'.
        """
        import sqlite3 as _sqlite3

        db_file = tmp_path / "legacy.db"
        # Create old-schema table without status
        conn = _sqlite3.connect(str(db_file))
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT INTO todos (title, completed) VALUES ('Old task', 0)")
        conn.execute("INSERT INTO todos (title, completed) VALUES ('Done task', 1)")
        conn.commit()
        conn.close()

        # Now run init_db() against this legacy DB
        models.DB_PATH = str(db_file)
        models.init_db()

        # Verify backfill
        result_conn = models.get_db()
        rows = result_conn.execute("SELECT title, completed, status FROM todos ORDER BY id").fetchall()
        assert rows[0]["status"] == "todo",  "Active task should be backfilled to 'todo'"
        assert rows[1]["status"] == "done",  "Completed task should be backfilled to 'done'"
        result_conn.close()


# ---------------------------------------------------------------------------
# GET /api/todos/stats
# ---------------------------------------------------------------------------

class TestGetStats:
    def test_empty_db_returns_all_zeros(self, client):
        resp = client.get("/api/todos/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {
            "total": 0,
            "completed": 0,
            "active": 0,
            "completion_rate": 0.0,
            "created_last_7_days": 0,
            "completed_last_7_days": 0,
        }

    def test_correct_totals_and_completion_rate(self, client):
        # 2 active, 1 completed
        client.post("/api/todos", json={"title": "Task A"})
        client.post("/api/todos", json={"title": "Task B"})
        client.post("/api/todos", json={"title": "Task C", "status": "done"})

        resp = client.get("/api/todos/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 3
        assert data["completed"] == 1
        assert data["active"] == 2
        assert data["completion_rate"] == round(1 / 3 * 100, 1)

    def test_all_completed_gives_100_percent(self, client):
        client.post("/api/todos", json={"title": "Done 1", "status": "done"})
        client.post("/api/todos", json={"title": "Done 2", "status": "done"})

        resp = client.get("/api/todos/stats")
        data = resp.get_json()
        assert data["total"] == 2
        assert data["completed"] == 2
        assert data["active"] == 0
        assert data["completion_rate"] == 100.0

    def test_recently_created_todos_counted(self, client):
        # Todos created via the API are always within the last 7 days
        client.post("/api/todos", json={"title": "New 1"})
        client.post("/api/todos", json={"title": "New 2"})

        resp = client.get("/api/todos/stats")
        data = resp.get_json()
        assert data["created_last_7_days"] == 2

    def test_completed_last_7_days_counts_completed_recent_todos(self, client):
        client.post("/api/todos", json={"title": "Recent done", "status": "done"})
        client.post("/api/todos", json={"title": "Recent active"})

        resp = client.get("/api/todos/stats")
        data = resp.get_json()
        assert data["completed_last_7_days"] == 1

    def test_old_todos_not_counted_in_7_day_window(self, client):
        """Todos with a created_at in the distant past should not appear in 7-day counts."""
        import sqlite3, models
        # Insert an old completed todo directly into the DB
        with sqlite3.connect(models.DB_PATH) as conn:
            conn.execute(
                "INSERT INTO todos (title, completed, status, created_at) VALUES (?, 1, 'done', ?)",
                ("Old done", "2000-01-01 00:00:00"),
            )
            conn.commit()

        resp = client.get("/api/todos/stats")
        data = resp.get_json()
        assert data["total"] == 1
        assert data["completed"] == 1
        assert data["created_last_7_days"] == 0
        assert data["completed_last_7_days"] == 0
