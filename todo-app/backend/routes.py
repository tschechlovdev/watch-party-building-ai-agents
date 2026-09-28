from flask import Blueprint, jsonify, request
from models import get_db, VALID_STATUSES

todos_bp = Blueprint("todos", __name__, url_prefix="/api/todos")


def _resolve_status_completed(status=None, completed=None, existing_status="todo"):
    """Apply the status/completed sync rule.

    Rules (status takes precedence when both are provided):
    - status='done'                  → completed=True
    - status='todo'|'in_progress'    → completed=False
    - completed=True  (no status)    → status='done'
    - completed=False (no status)    → status='todo' unless existing is 'in_progress'
    Returns (resolved_status, resolved_completed_int).
    """
    if status is not None:
        resolved_status = status
        resolved_completed = 1 if status == "done" else 0
    elif completed is not None:
        if completed:
            resolved_status = "done"
            resolved_completed = 1
        else:
            # Preserve in_progress when un-completing
            resolved_status = existing_status if existing_status == "in_progress" else "todo"
            resolved_completed = 0
    else:
        return None, None  # Nothing to resolve
    return resolved_status, resolved_completed


def todo_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "status": row["status"],
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

    status = data.get("status", "todo")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    completed = 1 if status == "done" else 0

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, completed, status) VALUES (?, ?, ?)",
            (title, completed, status),
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

        fields = {}

        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return jsonify({"error": "title must not be empty"}), 400
            fields["title"] = title

        # Validate status if provided
        new_status = data.get("status")
        if new_status is not None and new_status not in VALID_STATUSES:
            return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

        new_completed = data.get("completed")

        resolved_status, resolved_completed = _resolve_status_completed(
            status=new_status,
            completed=new_completed,
            existing_status=existing["status"],
        )
        if resolved_status is not None:
            fields["status"] = resolved_status
            fields["completed"] = resolved_completed

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
