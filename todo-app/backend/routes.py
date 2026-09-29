from flask import Blueprint, jsonify, request
from models import get_db

todos_bp = Blueprint("todos", __name__, url_prefix="/api/todos")


def todo_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
    }


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

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title) VALUES (?)", (title,)
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
        if "completed" in data:
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
