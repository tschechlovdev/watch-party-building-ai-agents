import sqlite3

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
# Status (Kanban board)
# ---------------------------------------------------------------------------

class TestStatusOnCreateAndGet:
    def test_default_status_is_todo(self, client):
        body = client.post("/api/todos", json={"title": "A"}).get_json()
        assert body["status"] == "todo"
        assert body["completed"] is False

    def test_get_returns_status_on_every_item(self, client):
        client.post("/api/todos", json={"title": "A"})
        client.post("/api/todos", json={"title": "B", "status": "in_progress"})
        items = client.get("/api/todos").get_json()
        assert {t["status"] for t in items} == {"todo", "in_progress"}

    def test_create_with_in_progress(self, client):
        resp = client.post("/api/todos",
                           json={"title": "A", "status": "in_progress"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_create_with_done_sets_completed(self, client):
        resp = client.post("/api/todos", json={"title": "A", "status": "done"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "done"
        assert body["completed"] is True

    @pytest.mark.parametrize("bad", ["bogus", 123, None, ""])
    def test_create_rejects_invalid_status(self, client, bad):
        resp = client.post("/api/todos", json={"title": "A", "status": bad})
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json() == []


class TestStatusOnUpdate:
    def _create(self, client, **extra):
        return client.post("/api/todos",
                           json={"title": "Original", **extra}).get_json()

    def _put(self, client, todo, **payload):
        return client.put(f"/api/todos/{todo['id']}", json=payload)

    def test_status_done_sets_completed_true(self, client):
        todo = self._create(client)
        body = self._put(client, todo, status="done").get_json()
        assert body["status"] == "done"
        assert body["completed"] is True

    @pytest.mark.parametrize("target", ["todo", "in_progress"])
    def test_status_non_done_sets_completed_false(self, client, target):
        todo = self._create(client, status="done")
        body = self._put(client, todo, status=target).get_json()
        assert body["status"] == target
        assert body["completed"] is False

    def test_status_persisted(self, client):
        todo = self._create(client)
        self._put(client, todo, status="in_progress")
        items = client.get("/api/todos").get_json()
        assert items[0]["status"] == "in_progress"

    @pytest.mark.parametrize("bad", ["bogus", 123, None])
    def test_update_rejects_invalid_status(self, client, bad):
        todo = self._create(client)
        resp = self._put(client, todo, status=bad)
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json()[0]["status"] == "todo"

    def test_update_unknown_id_with_status_returns_404(self, client):
        resp = client.put("/api/todos/999", json={"status": "done"})
        assert resp.status_code == 404

    def test_completed_false_on_in_progress_keeps_status(self, client):
        todo = self._create(client, status="in_progress")
        body = self._put(client, todo, completed=False).get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_title_only_update_keeps_done_state(self, client):
        todo = self._create(client, status="done")
        body = self._put(client, todo, title="Renamed").get_json()
        assert body["title"] == "Renamed"
        assert body["completed"] is True
        assert body["status"] == "done"

    def test_status_only_update_keeps_title(self, client):
        todo = self._create(client)
        body = self._put(client, todo, status="in_progress").get_json()
        assert body["title"] == "Original"

    def test_status_wins_over_conflicting_completed(self, client):
        todo = self._create(client)
        body = self._put(client, todo, status="todo", completed=True).get_json()
        assert body["status"] == "todo"
        assert body["completed"] is False

    def test_empty_payload_changes_nothing(self, client):
        todo = self._create(client, status="done")
        resp = self._put(client, todo)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "done"
        assert body["completed"] is True


class TestLegacyMigration:
    def test_existing_rows_get_status_without_data_loss(self, tmp_path):
        db_file = tmp_path / "legacy.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT INTO todos (title, completed) VALUES ('open', 0)")
        conn.execute("INSERT INTO todos (title, completed) VALUES ('closed', 1)")
        conn.commit()
        conn.close()

        models.DB_PATH = str(db_file)
        models.init_db()
        # Second call must be idempotent.
        models.init_db()

        app.config["TESTING"] = True
        with app.test_client() as client:
            items = {t["title"]: t for t in client.get("/api/todos").get_json()}
        assert len(items) == 2
        assert items["open"]["status"] == "todo"
        assert items["open"]["completed"] is False
        assert items["closed"]["status"] == "done"
        assert items["closed"]["completed"] is True


# ---------------------------------------------------------------------------
# Due dates
# ---------------------------------------------------------------------------

INVALID_DUE_DATES = [
    "2025-02-30", "15-06-2025", "2025-6-15", "20250615",
    "not-a-date", "", 123, True, ["2025-06-15"],
]


class TestDueDateOnCreateAndGet:
    def test_create_without_due_date_is_null(self, client):
        body = client.post("/api/todos", json={"title": "A"}).get_json()
        assert body["due_date"] is None

    def test_create_with_explicit_null(self, client):
        resp = client.post("/api/todos", json={"title": "A", "due_date": None})
        assert resp.status_code == 201
        assert resp.get_json()["due_date"] is None

    def test_create_with_due_date(self, client):
        resp = client.post("/api/todos",
                           json={"title": "A", "due_date": "2025-06-15"})
        assert resp.status_code == 201
        assert resp.get_json()["due_date"] == "2025-06-15"

    def test_get_returns_due_date_on_every_item(self, client):
        client.post("/api/todos", json={"title": "A"})
        client.post("/api/todos", json={"title": "B", "due_date": "2025-06-15"})
        items = client.get("/api/todos").get_json()
        assert all("due_date" in t for t in items)
        assert {t["due_date"] for t in items} == {None, "2025-06-15"}

    @pytest.mark.parametrize("bad", INVALID_DUE_DATES)
    def test_create_rejects_invalid_due_date(self, client, bad):
        resp = client.post("/api/todos", json={"title": "A", "due_date": bad})
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json() == []


class TestDueDateOnUpdate:
    def _create(self, client, **extra):
        return client.post("/api/todos",
                           json={"title": "Original", **extra}).get_json()

    def _put(self, client, todo, **payload):
        return client.put(f"/api/todos/{todo['id']}", json=payload)

    def test_sets_due_date(self, client):
        todo = self._create(client)
        body = self._put(client, todo, due_date="2025-06-15").get_json()
        assert body["due_date"] == "2025-06-15"
        assert client.get("/api/todos").get_json()[0]["due_date"] == "2025-06-15"

    def test_changes_due_date(self, client):
        todo = self._create(client, due_date="2025-06-15")
        body = self._put(client, todo, due_date="2025-07-01").get_json()
        assert body["due_date"] == "2025-07-01"

    @pytest.mark.parametrize("payload", [
        {"title": "Renamed"},
        {"status": "in_progress"},
        {"status": "done"},
        {"completed": True},
        {},
    ])
    def test_omitted_due_date_is_preserved(self, client, payload):
        todo = self._create(client, due_date="2025-06-15")
        body = self._put(client, todo, **payload).get_json()
        assert body["due_date"] == "2025-06-15"

    @pytest.mark.parametrize("bad", INVALID_DUE_DATES)
    def test_update_rejects_invalid_due_date(self, client, bad):
        todo = self._create(client, due_date="2025-06-15")
        resp = self._put(client, todo, due_date=bad)
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json()[0]["due_date"] == "2025-06-15"

    def test_update_unknown_id_with_due_date_returns_404(self, client):
        resp = client.put("/api/todos/999", json={"due_date": "2025-06-15"})
        assert resp.status_code == 404


class TestDueDateMigration:
    @staticmethod
    def _load_items(db_file):
        models.DB_PATH = str(db_file)
        models.init_db()
        # Second call must be idempotent.
        models.init_db()
        app.config["TESTING"] = True
        with app.test_client() as client:
            return client.get("/api/todos").get_json()

    def test_legacy_db_without_status_and_due_date(self, tmp_path):
        db_file = tmp_path / "legacy_no_status.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT INTO todos (title, completed) VALUES ('open', 0)")
        conn.commit()
        conn.close()

        items = self._load_items(db_file)
        assert len(items) == 1
        assert items[0]["title"] == "open"
        assert items[0]["due_date"] is None

    def test_db_with_status_but_without_due_date(self, tmp_path):
        db_file = tmp_path / "legacy_status.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                status     TEXT    NOT NULL DEFAULT 'todo'
            )
        """)
        conn.execute(
            "INSERT INTO todos (title, completed, status)"
            " VALUES ('closed', 1, 'done')"
        )
        conn.commit()
        conn.close()

        items = self._load_items(db_file)
        assert len(items) == 1
        assert items[0]["status"] == "done"
        assert items[0]["completed"] is True
        assert items[0]["due_date"] is None


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

class TestPriorityOnCreateAndGet:
    def test_default_priority_is_medium(self, client):
        resp = client.post("/api/todos", json={"title": "A"})
        assert resp.status_code == 201
        assert resp.get_json()["priority"] == "medium"

    @pytest.mark.parametrize("level", ["low", "medium", "high"])
    def test_create_with_each_valid_priority(self, client, level):
        resp = client.post("/api/todos", json={"title": "A", "priority": level})
        assert resp.status_code == 201
        assert resp.get_json()["priority"] == level

    @pytest.mark.parametrize("bad", ["bogus", 123, None, "", "HIGH"])
    def test_create_rejects_invalid_priority(self, client, bad):
        resp = client.post("/api/todos", json={"title": "A", "priority": bad})
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json() == []

    def test_get_returns_priority_on_every_item(self, client):
        client.post("/api/todos", json={"title": "A", "priority": "high"})
        client.post("/api/todos", json={"title": "B", "priority": "low"})
        client.post("/api/todos", json={"title": "C"})
        items = client.get("/api/todos").get_json()
        assert len(items) == 3
        assert all(t["priority"] in ("low", "medium", "high") for t in items)
        assert {t["title"]: t["priority"] for t in items} == {
            "A": "high", "B": "low", "C": "medium",
        }


class TestPriorityOnUpdate:
    def _create(self, client, **extra):
        return client.post("/api/todos",
                           json={"title": "Original", **extra}).get_json()

    def _put(self, client, todo, **payload):
        return client.put(f"/api/todos/{todo['id']}", json=payload)

    def test_update_priority_only_leaves_other_fields(self, client):
        todo = self._create(client, status="in_progress")
        resp = self._put(client, todo, priority="high")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["priority"] == "high"
        assert body["title"] == "Original"
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_update_priority_persisted(self, client):
        todo = self._create(client)
        self._put(client, todo, priority="low")
        assert client.get("/api/todos").get_json()[0]["priority"] == "low"

    def test_other_updates_keep_priority(self, client):
        todo = self._create(client, priority="high")
        body = self._put(client, todo, title="Renamed", completed=True).get_json()
        assert body["priority"] == "high"

    @pytest.mark.parametrize("bad", ["bogus", 123, None, "", "HIGH"])
    def test_update_rejects_invalid_priority(self, client, bad):
        todo = self._create(client, priority="high")
        resp = self._put(client, todo, priority=bad)
        assert resp.status_code == 400
        assert "error" in resp.get_json()
        assert client.get("/api/todos").get_json()[0]["priority"] == "high"

    def test_invalid_priority_with_valid_title_persists_neither(self, client):
        todo = self._create(client)
        resp = self._put(client, todo, title="Changed", priority="bogus")
        assert resp.status_code == 400
        item = client.get("/api/todos").get_json()[0]
        assert item["title"] == "Original"
        assert item["priority"] == "medium"

    def test_update_unknown_id_with_priority_returns_404(self, client):
        resp = client.put("/api/todos/999", json={"priority": "high"})
        assert resp.status_code == 404


class TestLegacyPriorityMigration:
    def _items_after_migration(self, db_file):
        models.DB_PATH = str(db_file)
        models.init_db()
        # Second call must be idempotent.
        models.init_db()
        app.config["TESTING"] = True
        with app.test_client() as client:
            return {t["title"]: t for t in client.get("/api/todos").get_json()}

    def test_rows_with_status_but_no_priority_default_to_medium(self, tmp_path):
        db_file = tmp_path / "legacy_status.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                status     TEXT    NOT NULL DEFAULT 'todo'
            )
        """)
        conn.execute("INSERT INTO todos (title, status) VALUES ('open', 'todo')")
        conn.execute(
            "INSERT INTO todos (title, completed, status) "
            "VALUES ('closed', 1, 'done')"
        )
        conn.commit()
        conn.close()

        items = self._items_after_migration(db_file)
        assert len(items) == 2
        assert items["open"]["priority"] == "medium"
        assert items["open"]["status"] == "todo"
        assert items["closed"]["priority"] == "medium"
        assert items["closed"]["status"] == "done"
        assert items["closed"]["completed"] is True

    def test_rows_with_neither_status_nor_priority_are_migrated(self, tmp_path):
        db_file = tmp_path / "legacy_both.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT INTO todos (title, completed) VALUES ('open', 0)")
        conn.execute("INSERT INTO todos (title, completed) VALUES ('closed', 1)")
        conn.commit()
        conn.close()

        items = self._items_after_migration(db_file)
        assert len(items) == 2
        assert items["open"]["priority"] == "medium"
        assert items["open"]["status"] == "todo"
        assert items["closed"]["priority"] == "medium"
        assert items["closed"]["status"] == "done"


# ---------------------------------------------------------------------------
# Generic 404
# ---------------------------------------------------------------------------

class TestNotFound:
    def test_unknown_route_returns_json_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}
