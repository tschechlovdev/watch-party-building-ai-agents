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

    def test_new_todo_has_status_todo(self, client):
        resp = client.post("/api/todos", json={"title": "New task"})
        assert resp.status_code == 201
        assert resp.get_json()["status"] == "todo"

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

    # --- status field tests ---

    def test_set_status_in_progress(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "in_progress"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False

    def test_set_status_done_sets_completed_true(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "done"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "done"
        assert body["completed"] is True

    def test_set_status_todo_sets_completed_false(self, client):
        todo = self._create(client)
        # First mark done
        client.put(f"/api/todos/{todo['id']}", json={"status": "done"})
        # Then move back to todo
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "todo"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "todo"
        assert body["completed"] is False

    def test_set_completed_true_sets_status_done(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": True})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["completed"] is True
        assert body["status"] == "done"

    def test_set_completed_false_sets_status_todo(self, client):
        todo = self._create(client)
        # First complete it
        client.put(f"/api/todos/{todo['id']}", json={"completed": True})
        # Then uncomplete
        resp = client.put(f"/api/todos/{todo['id']}", json={"completed": False})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["completed"] is False
        assert body["status"] == "todo"

    def test_invalid_status_returns_400(self, client):
        todo = self._create(client)
        resp = client.put(f"/api/todos/{todo['id']}", json={"status": "urgent"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_status_takes_precedence_over_completed(self, client):
        """When both status and completed are provided, status wins."""
        todo = self._create(client)
        # status=in_progress should override completed=True
        resp = client.put(f"/api/todos/{todo['id']}",
                          json={"status": "in_progress", "completed": True})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "in_progress"
        assert body["completed"] is False


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
