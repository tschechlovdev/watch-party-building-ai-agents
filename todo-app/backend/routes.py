import re
from datetime import date

from flask import Blueprint, jsonify, request
from models import get_db, VALID_STATUSES, VALID_PRIORITIES

todos_bp = Blueprint("todos", __name__, url_prefix="/api/todos")

STATUS_ERROR = "status must be one of: todo, in_progress, done"
PRIORITY_ERROR = "priority must be one of: low, medium, high"
DUE_DATE_ERROR = "due_date must be a valid date in YYYY-MM-DD format or null"


def todo_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "status": row["status"],
        "priority": row["priority"],
        "created_at": row["created_at"],
        "due_date": row["due_date"],
    }


def _invalid_status(data):
    if "status" not in data:
        return False
    status = data["status"]
    return not isinstance(status, str) or status not in VALID_STATUSES


def _invalid_priority(data):
    if "priority" not in data:
        return False
    priority = data["priority"]
    return not isinstance(priority, str) or priority not in VALID_PRIORITIES


def _invalid_due_date(data):
    if "due_date" not in data or data["due_date"] is None:
        return False
    value = data["due_date"]
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        return True
    try:
        date.fromisoformat(value)
    except ValueError:
        return True
    return False


@todos_bp.get("")
def list_todos():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM todos ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return jsonify([todo_to_dict(r) for r in rows]), 200


@todos_bp.post("")
def create_todo():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    if _invalid_status(data):
        return jsonify({"error": STATUS_ERROR}), 400
    if _invalid_priority(data):
        return jsonify({"error": PRIORITY_ERROR}), 400
    if _invalid_due_date(data):
        return jsonify({"error": DUE_DATE_ERROR}), 400

    status = data.get("status", "todo")
    priority = data.get("priority", "medium")
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, status, completed, priority, due_date)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                title,
                status,
                1 if status == "done" else 0,
                priority,
                data.get("due_date"),
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return jsonify(todo_to_dict(row)), 201


@todos_bp.put("/<int:todo_id>")
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}

    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "Not found"}), 404

        # Build update from only the fields provided
        fields = {}
        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return jsonify({"error": "title must not be empty"}), 400
            fields["title"] = title
        if _invalid_status(data):
            return jsonify({"error": STATUS_ERROR}), 400
        if _invalid_priority(data):
            return jsonify({"error": PRIORITY_ERROR}), 400
        if "priority" in data:
            fields["priority"] = data["priority"]
        if _invalid_due_date(data):
            return jsonify({"error": DUE_DATE_ERROR}), 400

        if data.get("due_date"):
            fields["due_date"] = data["due_date"]

        if "status" in data:
            fields["status"] = data["status"]
            fields["completed"] = 1 if data["status"] == "done" else 0
        elif "completed" in data:
            fields["completed"] = 1 if data["completed"] else 0

        if fields:
            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [todo_id]
            conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)  # noqa: S608
            conn.commit()

        row = conn.execute(
            "SELECT * FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
    return jsonify(todo_to_dict(row)), 200


@todos_bp.delete("/<int:todo_id>")
def delete_todo(todo_id):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "Not found"}), 404
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return "", 204
