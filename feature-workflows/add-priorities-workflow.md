---
feature: "Todo Priorities"
slug: "add-priorities"
feature-request-file: "feature-requests/add-priorities.md"
current-role: done
needs-architect: true
branch: "feature/add-priorities"
---

# Feature Workflow: Todo Priorities

## PM Analysis

_Filled in by the PM Agent._

### User Stories

1. As a todo user, I want to optionally set a priority (low, medium, or high) when I create a todo, so that I can signal its urgency from the start.
2. As a todo user, I want to change the priority of an existing todo, so that I can re-triage my list as circumstances change.
3. As a todo user, I want each todo to show a visual priority indicator (e.g. a colour-coded badge), so that I can see at a glance which items matter most.
4. As a todo user, I want to filter my list to show only todos of a given priority, so that I can focus on what matters most first.
5. As an existing user with todos created before this feature, I want my old todos to keep working and default to medium priority, so that I don't lose or have to re-enter any data.

### Acceptance Criteria

1. Valid priority values are exactly `low`, `medium`, and `high`.
2. Every todo has a priority. Todos created without a priority default to `medium`.
3. Existing todos in the database (created before this feature) are migrated to `medium` without data loss; the migration is safe to run repeatedly (idempotent), consistent with the existing `status` migration in `init_db`.
4. `POST /api/todos` accepts an optional `priority` field. When provided and valid, the created todo has that priority; when omitted, it is `medium`.
5. `PUT /api/todos/<id>` accepts a `priority` field and updates only the priority when it is the only field sent; other fields are left unchanged.
6. `POST` and `PUT` with an invalid `priority` (not one of the three values, wrong type, or empty string) return HTTP 400 with a JSON `{"error": "..."}` message, and no change is persisted.
7. All todo JSON responses (`GET`, `POST`, `PUT`) include a `priority` field with one of the three valid values.
8. The create-todo UI lets the user choose a priority (low / medium / high), pre-selected to `medium`, and submitting without touching it creates a `medium` todo.
9. The priority of an existing todo can be changed from the UI, and the change is persisted via the API and reflected immediately without a page reload.
10. Each todo displays a visually distinct priority indicator (badge or colour-coded label) that differs for `low`, `medium`, and `high` and includes a text label (not colour alone). The indicator appears in the list view and on Kanban cards.
11. The UI provides a priority filter with options All, High, Medium, and Low. Selecting a priority shows only todos with that priority; selecting All shows every todo. Default is All.
12. The filter applies to both the List and Board views, and the "completed / total" counter behaviour remains consistent and non-broken when a filter is active.
13. Sorting by priority, if offered, is done client-side only; no server-side priority sorting is added. The existing default ordering (newest first) is unchanged.
14. Backend tests cover: default priority, create with each valid priority, create with invalid priority, update priority, update with invalid priority, priority present in list responses, and migration of pre-existing rows. Existing tests continue to pass.

### Out of Scope

- Priority-based notifications or reminders.
- Custom priority labels or additional priority levels beyond `low`, `medium`, `high`.
- Automatic prioritisation by AI.
- Server-side priority sorting or server-side filtering (client-side only for v1; client-side sort is optional, not required).
- Changing the existing status/Kanban column behaviour or the default newest-first ordering.
- Persisting the selected filter across page reloads.
- Bulk priority editing.

### Branch

`feature/add-priorities` (existing; created by the Orchestrator — no new branch created by the PM Agent).

---

## Architecture Design

_Filled in by the Architect Agent._

> Note: the backend uses raw `sqlite3` (see `todo-app/backend/models.py`), not SQLAlchemy. There is no ORM model or migration tool; schema changes live in `init_db()`.

### DB Schema Changes

Add one column to the `todos` table:

| Column     | Type | Nullable | Default    |
|------------|------|----------|------------|
| `priority` | TEXT | NOT NULL | `'medium'` |

- `models.py`: add the constant `VALID_PRIORITIES = ("low", "medium", "high")` next to `VALID_STATUSES`.
- `models.py` `init_db()`:
  - Add `priority TEXT NOT NULL DEFAULT 'medium'` to the `CREATE TABLE IF NOT EXISTS todos` statement (fresh databases).
  - After the existing `status` migration block, add an idempotent migration using the already-computed `columns` list (re-read it with a fresh `PRAGMA table_info(todos)` after the status block, since the status block may have just added a column):
    ```python
    if "priority" not in columns:
        conn.execute(
            "ALTER TABLE todos ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'"
        )
    ```
  - SQLite back-fills existing rows with the constant default `'medium'`, so no separate `UPDATE` is needed. The `if "priority" not in columns` guard makes repeated runs safe (same pattern as `status`).
- No CHECK constraint is added, consistent with the existing `status` column; validation is enforced in the route layer.

### API Changes

All changes are in `todo-app/backend/routes.py`. No new endpoints; no changes to `app.py`.

**Shared helpers**
- Import `VALID_PRIORITIES` from `models`.
- Add `PRIORITY_ERROR = "priority must be one of: low, medium, high"`.
- Add `_invalid_priority(data)` mirroring `_invalid_status`: returns `False` if `"priority"` not in `data`; otherwise returns `True` when the value is not a `str` or not in `VALID_PRIORITIES` (so `None`, `123`, `""`, `"urgent"`, and wrong case such as `"HIGH"` are all invalid).
- `todo_to_dict(row)`: add `"priority": row["priority"]`.

**`GET /api/todos`**
- Unchanged behaviour and ordering (`created_at DESC, id DESC`). Each item now includes `priority`. `SELECT *` already returns the new column.

**`POST /api/todos`**
- Request body: `title` (string, required, unchanged); `status` (optional, unchanged); **`priority`** (string, optional, one of `low|medium|high`, default `medium`).
- Validation: after the title and status checks, `if _invalid_priority(data): return jsonify({"error": PRIORITY_ERROR}), 400` (before any INSERT, so nothing is persisted).
- `priority = data.get("priority", "medium")`; extend the INSERT to `INSERT INTO todos (title, status, completed, priority) VALUES (?, ?, ?, ?)`.
- Response: `201` with `{id, title, completed, status, priority, created_at}`.
- Errors: `400 {"error": "title is required"}`, `400 {"error": STATUS_ERROR}`, `400 {"error": PRIORITY_ERROR}`.

**`PUT /api/todos/<id>`**
- Request body: any subset of `title`, `status`, `completed`, **`priority`** (string, one of the three values).
- Validation: after the existing status check and before building/executing the UPDATE, `if _invalid_priority(data): return jsonify({"error": PRIORITY_ERROR}), 400`. Because the UPDATE is only executed at the end, an invalid priority persists nothing (including when combined with a valid title).
- `if "priority" in data: fields["priority"] = data["priority"]`. The existing dynamic `SET` clause builder handles it; sending only `priority` leaves title/status/completed untouched.
- Response: `200` with the full todo dict including `priority`.
- Errors: `404 {"error": "Not found"}` (unknown id, checked first, unchanged), `400` for invalid title / status / priority.

**`DELETE /api/todos/<id>`** — unchanged.

No server-side filtering or sorting by priority is added (out of scope).

### Frontend Changes

Stack: React + Tailwind (utility classes). Tailwind class names must appear as complete literal strings (no string interpolation of partial class names).

**New file `todo-app/frontend/src/priority.js`** (shared constants):
- `export const PRIORITIES = ['low', 'medium', 'high']`
- `export const PRIORITY_LABELS = { low: 'Low', medium: 'Medium', high: 'High' }`
- `export const PRIORITY_STYLES` mapping each value to full literal Tailwind classes, e.g. `low` → `bg-green-100 text-green-800 border-green-300`, `medium` → `bg-yellow-100 text-yellow-800 border-yellow-300`, `high` → `bg-red-100 text-red-800 border-red-300`.

**New component `todo-app/frontend/src/components/PriorityBadge.jsx`**:
- Props: `{ priority }`. Renders `<span>` with rounded-full pill classes plus `PRIORITY_STYLES[priority]` and the text `PRIORITY_LABELS[priority]` (text label, not colour alone). Fall back to `medium` if the value is unknown.

**`api.js`**
- `createTodo(title, priority)` → body `JSON.stringify({ title, priority })`. `updateTodo` is unchanged (already sends arbitrary fields, e.g. `{ priority: 'high' }`).

**`AddTodo.jsx`**
- Add state `priority` (initial `'medium'`) and a `<select aria-label="Priority">` with options from `PRIORITIES`/`PRIORITY_LABELS`, placed between the text input and the Add button.
- `handleSubmit` calls `onAdd(trimmed, priority)`. After submit, keep or reset the select to `'medium'` (reset to `'medium'` for predictability).

**`App.jsx`**
- `handleAdd(title, priority)` → `createTodo(title, priority)`.
- New state: `const [priorityFilter, setPriorityFilter] = useState('all')` (default All, not persisted).
- Derive `const visibleTodos = priorityFilter === 'all' ? todos : todos.filter((t) => t.priority === priorityFilter)`.
- Add a filter control row (below the List/Board toggle or beside the AddTodo form) with options `All`, `High`, `Medium`, `Low` (in that order), implemented like the existing view toggle: buttons with `aria-pressed` (or a `<select aria-label="Filter by priority">`). Use full-literal Tailwind classes.
- Pass `visibleTodos` (instead of `todos`) to both `TodoList` and `KanbanBoard`. Keep `handleUpdate`/`handleDelete` unchanged (they operate on the full `todos` state, so a todo whose priority is changed while a filter is active simply drops out of the filtered view after the update, which is expected).
- Counter: compute from `visibleTodos` so it matches what is displayed: `{visibleTodos.filter((t) => t.completed).length} / {visibleTodos.length} completed`. Keep the guard `todos.length > 0` for rendering the counter at all so it never disappears awkwardly; with an active filter that matches nothing it shows `0 / 0 completed`.
- Pass a new boolean prop `isFiltered={priorityFilter !== 'all'}` to `TodoList` for the empty state.
- No client-side sorting is added; default order (newest first) is untouched.

**`TodoList.jsx`**
- Accept `isFiltered` prop. When `todos.length === 0`: show `"No todos match this filter."` if `isFiltered`, otherwise the existing "No todos yet. Add one above!".

**`TodoItem.jsx`** (List view: indicator + change priority)
- Add a priority `<select aria-label="Priority" value={todo.priority} onChange={(e) => onUpdate(todo.id, { priority: e.target.value })}>` with the three options (text labels `Low`/`Medium`/`High`), styled with `PRIORITY_STYLES[todo.priority]` plus pill classes so it acts as the colour-coded indicator and the editor. Place it between the title and the delete button. The `onUpdate` → `handleUpdate` path replaces the todo in state with the server response, so the change shows without reload (AC 9).

**`KanbanCard.jsx`** (Board view: indicator only)
- Render `<PriorityBadge priority={todo.priority} />` before the delete button (after the title). No drag/drop changes. `KanbanBoard.jsx` needs no change: it already filters `todos` per column from the (now pre-filtered) prop, so column counts reflect the active filter, and `handleDrop` finds dragged cards in the visible list.

**State summary**: new `priorityFilter` in `App`; new `priority` in `AddTodo`; todo objects now carry `priority`.

### Engineer Checklist

Backend first.

1. In `todo-app/backend/models.py`, add `VALID_PRIORITIES = ("low", "medium", "high")` below `VALID_STATUSES`.
2. In `models.py` `init_db()`, add `priority TEXT NOT NULL DEFAULT 'medium'` to the `CREATE TABLE IF NOT EXISTS todos` statement.
3. In `models.py` `init_db()`, after the `status` migration block, re-read the columns with `PRAGMA table_info(todos)` and, if `"priority"` is missing, run `ALTER TABLE todos ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'`. Keep `conn.commit()` at the end.
4. In `todo-app/backend/routes.py`, change the import to `from models import get_db, VALID_STATUSES, VALID_PRIORITIES`.
5. Add `PRIORITY_ERROR = "priority must be one of: low, medium, high"` beside `STATUS_ERROR`.
6. Add `"priority": row["priority"]` to `todo_to_dict`.
7. Add `_invalid_priority(data)` mirroring `_invalid_status` (invalid when present and not a `str` in `VALID_PRIORITIES`).
8. In `create_todo`, after the status validation, return `400` with `PRIORITY_ERROR` if `_invalid_priority(data)`; read `priority = data.get("priority", "medium")` and include it in the INSERT (`INSERT INTO todos (title, status, completed, priority) VALUES (?, ?, ?, ?)`).
9. In `update_todo`, after the status validation and before building the UPDATE, return `400` with `PRIORITY_ERROR` if `_invalid_priority(data)`; add `if "priority" in data: fields["priority"] = data["priority"]`.
10. In `todo-app/backend/tests/test_routes.py`, add tests (new classes `TestPriority...`, following the existing style/fixtures):
    - default priority is `medium` on create without a priority;
    - create with each of `low`, `medium`, `high` (parametrized) returns 201 and that priority;
    - create rejects invalid priority (parametrize `"bogus"`, `123`, `None`, `""`, `"HIGH"`) with 400 + `error` key and nothing persisted (`GET` returns `[]`);
    - `GET /api/todos` includes `priority` on every item (mixed priorities);
    - update priority only (title/status/completed unchanged) and persisted on subsequent `GET`;
    - update rejects invalid priority (parametrized) with 400 and the stored priority stays unchanged;
    - update with invalid priority plus a valid title persists neither;
    - unknown id with priority returns 404;
    - migration test (`TestLegacyPriorityMigration`): build a legacy DB that has `status` but no `priority` column (and one that has neither), insert rows, call `models.init_db()` twice, and assert via the API that all rows keep their data and have `priority == "medium"`.
11. Run `cd todo-app/backend && uv run pytest` and make sure the backend tests all pass before touching the frontend.
12. Create `todo-app/frontend/src/priority.js` exporting `PRIORITIES`, `PRIORITY_LABELS`, and `PRIORITY_STYLES` (complete literal Tailwind class strings per priority; distinct colours for low/medium/high).
13. Create `todo-app/frontend/src/components/PriorityBadge.jsx` rendering a pill with the text label and `PRIORITY_STYLES[priority]` (fall back to `medium` when unknown).
14. In `todo-app/frontend/src/api.js`, change `createTodo` to `(title, priority) => request(BASE, { method: 'POST', body: JSON.stringify({ title, priority }) })`.
15. In `AddTodo.jsx`, add `priority` state (default `'medium'`), a `<select aria-label="Priority">` with Low/Medium/High options between the input and the Add button, call `onAdd(trimmed, priority)` on submit, and reset priority to `'medium'` after submit.
16. In `TodoItem.jsx`, add a colour-coded `<select aria-label="Priority">` (value `todo.priority`, options Low/Medium/High) between the title and the delete button that calls `onUpdate(todo.id, { priority: e.target.value })`.
17. In `KanbanCard.jsx`, import and render `<PriorityBadge priority={todo.priority} />` between the title and the delete button.
18. In `TodoList.jsx`, accept an `isFiltered` prop and show "No todos match this filter." instead of the default empty message when `isFiltered` is true and the list is empty.
19. In `App.jsx`, update `handleAdd` to `(title, priority)` and pass priority to `createTodo`.
20. In `App.jsx`, add `priorityFilter` state (default `'all'`) and derive `visibleTodos`; render a filter control with options All / High / Medium / Low (with `aria-pressed` buttons or a labelled select).
21. In `App.jsx`, pass `visibleTodos` to `TodoList` (plus `isFiltered={priorityFilter !== 'all'}`) and to `KanbanBoard`; keep `handleUpdate`/`handleDelete` on the full `todos` state.
22. In `App.jsx`, change the completed counter to use `visibleTodos` (`{visibleTodos.filter((t) => t.completed).length} / {visibleTodos.length} completed`), still rendered only when `todos.length > 0`.
23. Do not add any sorting and do not change `KanbanBoard.jsx` or the backend ordering.
24. Run `cd todo-app/frontend && npm run build` (if dependencies are installed) to confirm the frontend compiles; fix any errors.
25. Run `cd todo-app/backend && uv run pytest` and confirm all tests pass.

---

## Implementation Notes

_Filled in by the Engineer Agent._

### Changes Made

Backend:
- `todo-app/backend/models.py`: added `VALID_PRIORITIES`, the `priority TEXT NOT NULL DEFAULT 'medium'` column in `CREATE TABLE`, and an idempotent `ALTER TABLE` migration (guarded by a fresh `PRAGMA table_info`) so existing databases are back-filled with `medium`.
- `todo-app/backend/routes.py`: added `PRIORITY_ERROR`, `_invalid_priority`, `priority` in `todo_to_dict`, priority validation + insert in `POST`, and priority validation + update in `PUT` (400 on invalid values, nothing persisted).

Frontend:
- `todo-app/frontend/src/priority.js` (new): shared `PRIORITIES`, `PRIORITY_LABELS`, `PRIORITY_STYLES` (literal Tailwind classes: green = low, yellow = medium, red = high).
- `todo-app/frontend/src/components/PriorityBadge.jsx` (new): pill with text label; falls back to `medium` for unknown values.
- `todo-app/frontend/src/api.js`: `createTodo(title, priority)` sends the priority.
- `todo-app/frontend/src/components/AddTodo.jsx`: priority select (default Medium, reset after submit) passed to `onAdd`.
- `todo-app/frontend/src/components/TodoItem.jsx`: colour-coded priority select that both shows and changes the priority via `onUpdate`.
- `todo-app/frontend/src/components/KanbanCard.jsx`: shows `PriorityBadge`.
- `todo-app/frontend/src/components/TodoList.jsx`: new `isFiltered` prop for the "No todos match this filter." empty state.
- `todo-app/frontend/src/App.jsx`: `priorityFilter` state (All/High/Medium/Low, default All), `visibleTodos` passed to both List and Board views, `handleAdd(title, priority)`, completed counter based on visible todos. No sorting added; ordering unchanged.

### Tests

`todo-app/backend/tests/test_routes.py` (new classes):
- `TestPriorityOnCreateAndGet`: default `medium`, create with each valid level, invalid values rejected with 400 and nothing persisted (`"bogus"`, `123`, `None`, `""`, `"HIGH"`), `priority` present on all list items.
- `TestPriorityOnUpdate`: priority-only update leaves other fields unchanged, persisted, other updates keep priority, invalid values rejected and stored value unchanged, invalid priority + valid title persists neither, unknown id returns 404.
- `TestLegacyPriorityMigration`: legacy DBs with `status` but no `priority`, and with neither column, keep their data, get `priority == "medium"`, and `init_db()` is idempotent.

Frontend checks (no frontend test framework): `npm run lint` → 0 warnings, 0 errors; `npm run build` → succeeds.

### Test Run Result

```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-priorities/todo-app/backend
configfile: pyproject.toml
testpaths: tests
collected 61 items

tests/test_routes.py ................................................... [ 83%]
..........                                                               [100%]

============================== 61 passed in 0.21s ==============================
```

---

## Review Feedback

_Filled in by the Reviewer Agent._

### Issues Found

None.

### Verdict

Approved

---

## Outcome

All 14 acceptance criteria met; 61 backend tests pass. Feature fully implemented and approved.
