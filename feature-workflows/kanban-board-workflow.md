---
feature: "Kanban Board"
requester: "watch-party"
status: "complete"
current-role: "done"
needs-architect: true
---

# Feature Workflow

---

## Feature Request

# Feature Request: Kanban Board

## Summary

Users want a Kanban-style board view so they can visualise their todos as cards moving through
defined stages (e.g. To Do → In Progress → Done).

## Description

The current list view is fine for simple task tracking but doesn't support workflow-oriented work
where tasks have meaningful stages. A Kanban board groups todos into columns representing stages,
and users can move cards between columns by dragging or using a control.

## Desired Behaviour

- The UI offers a toggle between the existing list view and a new board view.
- The board view displays three columns: **To Do**, **In Progress**, **Done**.
- Each todo belongs to exactly one column based on its status.
- Users can move a todo to a different column (changing its status).
- Todos that are marked "completed" are automatically moved to (or reflected in) the Done column.
- The existing list view continues to work unchanged.
- A new `status` field is added to todos: `todo`, `in_progress`, or `done`.
- `done` status corresponds to `completed = true`; the two are kept in sync.

## Implementation Complexity Notes

This feature involves:
- A new `status` column in the DB (or a mapping from `completed` to `todo`/`done`)
- New API support for updating `status`
- A significant new frontend component (the board layout and column logic)
- Optional: drag-and-drop (can be deferred to v2; use a "Move to..." button for v1)

## Out of Scope

- Custom column names or adding more than three columns (v1 uses fixed columns)
- Swimlanes, labels, or story-point estimates on cards
- Drag-and-drop (v1 uses a move button; DnD is a v2 enhancement)
- Card comments or attachments
- WIP limits

---

## PM Analysis

### User Stories

1. As a user, I want to switch between a list view and a board view so that I can choose the visualisation that best fits how I'm working.
2. As a user, I want to see my todos grouped into **To Do**, **In Progress**, and **Done** columns so that I can understand the state of my work at a glance.
3. As a user, I want to move a todo to a different column so that I can update its stage as my work progresses.
4. As a user, I want newly created todos to appear in the **To Do** column by default so that I don't have to manually assign a starting status.
5. As a user, I want checking off a todo as "completed" to automatically move it to the **Done** column so that the board stays consistent with the list view.

### Acceptance Criteria

- [ ] The app header or top bar contains a toggle that switches between "List" view and "Board" view. The currently active view is visually indicated.
- [ ] The board view displays exactly three columns labelled **To Do**, **In Progress**, and **Done**, each showing the todos whose status matches that column.
- [ ] Each todo card in the board view shows at minimum its title and a way to move it to another column (e.g. a "Move to..." button or dropdown).
- [ ] Moving a todo from one column to another persists the change — a page refresh keeps the todo in its new column.
- [ ] When a todo is marked complete (via either the list view or the board view), its status becomes `done` and it appears in the Done column. When a todo is unchecked, its status reverts to `todo`.
- [ ] New todos created via the add form default to status `todo` and appear in the To Do column.
- [ ] The existing list view continues to function identically to today (no regressions in add, edit, complete, delete).

### Out of Scope

- Drag-and-drop between columns (v1 uses an explicit move control; DnD is a v2 enhancement)
- Custom column names or more than three columns
- Swimlanes, WIP limits, or story-point estimates
- Card comments, attachments, or expanded card details
- Sorting or filtering within board columns

### Architect Recommendation

**Needs Architect: Yes** — this feature requires a new `status` column in the SQLite database, a modified API contract for the `PUT /api/todos/:id` endpoint (to accept and return `status`), and a significant new frontend component (the board layout with three columns and a move control). The Architect should specify the exact DB migration strategy, the API shape including how `status` and `completed` are kept in sync, and which new/modified frontend components are needed.

---

## Architecture Design

<!-- ARCHITECT AGENT: Fill in this section.
- Read the PM Analysis above and the existing codebase (models.py, routes.py, api.js, App.jsx).
- Design the minimal changes needed to satisfy the acceptance criteria.
- Write design-only content — no implementation code, no code snippets.
- Flag any risks or open questions for the engineer.
- When done, set current-role to "engineer" in the front matter.
-->

### DB Schema Changes

Add a `status` column to the existing `todos` table using a migration applied at application
startup (inside `init_db()`):

```
ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'
```

Valid values: `'todo'`, `'in_progress'`, `'done'`.

The column defaults to `'todo'` so all existing rows receive a valid status without a data
migration script.

**Sync rule**: `status` and `completed` must stay consistent at all times:
- `status = 'done'`  ↔  `completed = 1`
- `status = 'todo'` or `status = 'in_progress'`  ↔  `completed = 0`

Enforcement happens in the API layer (see API Changes below), not in the DB.

### API Changes

**Modified: `PUT /api/todos/<id>`**

The endpoint already accepts partial updates via a `fields` dict. Two new fields are added:

1. `status` (string) — one of `'todo'`, `'in_progress'`, `'done'`. When provided:
   - Validate it is one of the three allowed values; return 400 if not.
   - Automatically set `completed` to `1` if `status == 'done'`, else `0`.
   - Store both `status` and `completed` in the same UPDATE query.

2. `completed` (boolean) — existing behaviour is preserved, but when `completed` is set:
   - If `completed = true`, automatically set `status = 'done'`.
   - If `completed = false`, automatically set `status = 'todo'` (not `'in_progress'`,
     since unchecking a completed item returns it to the backlog).

**Modified: `todo_to_dict(row)`**

Add `"status": row["status"]` to the returned dict. All existing responses (GET list, POST
create, PUT update) will now include the `status` field — no new endpoint needed.

**No new endpoints.** All changes are additive modifications to the existing PUT endpoint and
serialiser.

### Frontend Changes

**`todo-app/frontend/src/api.js`** — No changes needed. `updateTodo(id, fields)` already
accepts arbitrary fields; callers just need to pass `{ status: 'in_progress' }` etc.

**`todo-app/frontend/src/App.jsx`**

- Add a `view` state variable: `'list'` or `'board'` (default `'list'`).
- Add a `handleStatusChange(id, newStatus)` function that calls `updateTodo(id, { status })` and
  updates the local `todos` state the same way `handleUpdate` does.
- Render a view toggle (two buttons: "List" / "Board") below the heading and above the error banner.
- Conditionally render either `<TodoList>` (existing) or a new `<KanbanBoard>` component depending
  on `view`.
- Pass `todos`, `onUpdate`, `onDelete`, and `onStatusChange` to `<KanbanBoard>`.

**New component: `todo-app/frontend/src/components/KanbanBoard.jsx`**

- Accepts props: `todos`, `onUpdate`, `onDelete`, `onStatusChange`.
- Renders three columns side-by-side (Tailwind flex or grid layout):
  - **To Do** — todos where `status === 'todo'`
  - **In Progress** — todos where `status === 'in_progress'`
  - **Done** — todos where `status === 'done'`
- Each column header shows the column name and the count of cards in it.
- Each card renders the todo title. For non-Done columns, a "Move to…" select/dropdown lets the
  user pick the target column; on change it calls `onStatusChange(id, newStatus)`.
- Cards in the Done column show the title struck-through (same as the list view's completed style)
  and offer a "Move back to To Do" action (calls `onStatusChange(id, 'todo')`).
- No inline editing or delete in the board view for v1 (keep scope minimal).

**`todo-app/frontend/src/components/TodoItem.jsx`** (read before implementing)

- The existing `completed` toggle in the list view calls `onUpdate(id, { completed: !todo.completed })`.
- No changes needed to `TodoItem.jsx` — the API layer will automatically sync `status` when
  `completed` is set.

**`todo-app/frontend/src/components/TodoList.jsx`** — No changes needed.

### Engineer Checklist

1. **DB migration** — In `models.py` `init_db()`, add an `ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'` statement wrapped in a try/except (SQLite raises `OperationalError` if the column already exists; catch and ignore it so the app starts cleanly on both fresh and existing databases).

2. **`todo_to_dict`** — Add `"status": row["status"]` to the returned dict in `routes.py`.

3. **`update_todo` route** — Add handling for the `status` field in the `PUT` handler:
   - Accept `status` from the request body.
   - Validate it is `'todo'`, `'in_progress'`, or `'done'`; return 400 otherwise.
   - When `status` is provided, derive `completed` automatically (`1` if `'done'`, else `0`) and include both in the UPDATE query.
   - When `completed` is provided (but not `status`), derive `status` automatically (`'done'` if true, `'todo'` if false) and include both in the UPDATE query.
   - When both are provided, `status` takes precedence and `completed` is overridden accordingly.

4. **Backend tests** — Add tests in `tests/test_routes.py`:
   - New todo has `status: 'todo'` in the create response.
   - PUT with `status: 'in_progress'` returns `status: 'in_progress'` and `completed: false`.
   - PUT with `status: 'done'` returns `status: 'done'` and `completed: true`.
   - PUT with `completed: true` returns `completed: true` and `status: 'done'`.
   - PUT with `completed: false` returns `completed: false` and `status: 'todo'`.
   - PUT with invalid `status` value returns 400.

5. **`App.jsx`** — Add `view` state, view toggle buttons, `handleStatusChange` function, and conditional rendering of `<KanbanBoard>` vs `<TodoList>`.

6. **`KanbanBoard.jsx`** — Create the new component with three columns, card rendering, and move controls as described in Frontend Changes.

7. **Manual smoke test** — Verify: create a todo → appears in To Do column; move to In Progress → persists after refresh; move to Done → `completed` becomes true and is checked in list view; uncheck in list view → moves back to To Do in board view.

### Open Questions / Risks

1. **SQLite ALTER TABLE on existing DB** — SQLite does not support `ADD COLUMN ... NOT NULL` without a default when rows exist. The design uses `DEFAULT 'todo'` which is safe. The engineer must still guard against the `OperationalError: duplicate column name` on repeated startups.

2. **Status / completed sync on client** — If the engineer updates `completed` locally in `handleUpdate` without re-fetching, the local `status` field will be stale. The engineer must ensure the server response (which includes the updated `status`) is used to replace the local todo object — this is already the pattern in `handleUpdate` (`prev.map(t => t.id === id ? updated : t)`), so it should work as long as the API returns the full updated object.

3. **Board layout on small screens** — Three columns side-by-side may be cramped on mobile. For v1, a simple horizontal scroll or wrapping grid is acceptable; no responsive breakpoint design is required beyond what Tailwind defaults give.

4. **No delete or edit in board view** — Accepted as out of scope for v1. Cards in the board are read + move only.

---

## Implementation Notes

<!-- ENGINEER AGENT (first pass): Fill in this section after implementing the Architecture Design.
- List every file you changed and why.
- Briefly describe the approach taken.
- List the tests you added.
- Run `uv run pytest` from todo-app/backend/ and confirm tests pass before writing this section.
- When done, set current-role to "reviewer" in the front matter.

PASS DETECTION: If the Review Feedback section below is still empty, this is your first pass.
If Review Feedback is already filled in, skip this section and go to Improvement Notes instead.
-->

### Files Changed

- **`todo-app/backend/models.py`** — Added `ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'` inside `init_db()`, wrapped in a try/except to safely handle both fresh databases and existing ones where the column already exists.
- **`todo-app/backend/routes.py`** — Added `status` field to `todo_to_dict()`; updated `create_todo` to explicitly insert `status = 'todo'`; extended `update_todo` to accept and validate `status` (with `completed` derived automatically), and to derive `status` when only `completed` is provided.
- **`todo-app/backend/tests/test_routes.py`** — Added 8 new test cases covering the `status` field (see Tests Added below). All pre-existing tests retained and passing.
- **`todo-app/frontend/src/App.jsx`** — Added `view` state (`'list'` or `'board'`), a view toggle (two pill buttons), a `handleStatusChange` function, and conditional rendering of `<KanbanBoard>` vs `<TodoList>`. Max-width relaxed from `max-w-md` to `max-w-4xl` for the board layout.
- **`todo-app/frontend/src/components/KanbanBoard.jsx`** — New component. Renders three columns (To Do, In Progress, Done) using Tailwind flex layout. Each card shows its title and move buttons; Done column cards are struck through. Uses a `COLUMNS` config array and an `OTHER_COLUMNS` map to keep column definitions DRY.

### Approach

The backend change is additive: a new `status` column with a safe default means zero data migration is needed. The sync rule (status ↔ completed) is enforced in the API layer inside `update_todo` — `status` takes precedence when both fields are provided, otherwise the provided field drives the other. On the frontend, `App.jsx` gains a minimal view toggle and a `handleStatusChange` callback that calls the existing `updateTodo` API function with `{ status }`. The `KanbanBoard` component is self-contained and receives only read + action props from `App.jsx`, matching the existing pattern used by `TodoList`.

### Tests Added

- `TestCreateTodo::test_new_todo_has_status_todo` — new todos default to `status: 'todo'`
- `TestUpdateTodo::test_set_status_in_progress` — PUT with `status: 'in_progress'` returns `status: 'in_progress'` and `completed: false`
- `TestUpdateTodo::test_set_status_done_sets_completed_true` — PUT with `status: 'done'` returns `completed: true`
- `TestUpdateTodo::test_set_status_todo_sets_completed_false` — moving back to `todo` sets `completed: false`
- `TestUpdateTodo::test_set_completed_true_sets_status_done` — PUT with `completed: true` derives `status: 'done'`
- `TestUpdateTodo::test_set_completed_false_sets_status_todo` — PUT with `completed: false` derives `status: 'todo'`
- `TestUpdateTodo::test_invalid_status_returns_400` — unknown status value returns 400 with error message
- `TestUpdateTodo::test_status_takes_precedence_over_completed` — when both provided, `status` wins

---

## Review Feedback

<!-- REVIEWER AGENT: Fill in this section.
- Read the PM Analysis, Architecture Design, and Implementation Notes sections above.
- Read every file listed under "Files Changed".
- Categorize issues as Blocking (must fix) or Suggestions (optional improvement).
- Check: correctness, test coverage, security (no hardcoded secrets, no 0.0.0.0 binding),
  API contract consistency with the Architecture Design, frontend error handling, code style.
- Give a final verdict: Approved or Changes Required.
- If Changes Required: set current-role to "engineer" in the front matter.
- If Approved: set current-role to "done" in the front matter.
-->

### Blocking Issues

None.

### Suggestions

- **Suggestion:** `KanbanBoard.jsx` — the Architecture Design specified `onUpdate` and `onDelete` props, but the implementation intentionally omits them (board is read + move only for v1). This is the correct v1 behaviour and consistent with the out-of-scope list, but the prop signature in the Architecture Design could be updated in a follow-up for documentation accuracy.
- **Suggestion:** `routes.py` line 81 — the `f"UPDATE todos SET {set_clause} WHERE id = ?"` string is built from controlled dict keys (never from user-supplied input), which is safe. A future refactor could use a mapping to a fixed allowed-columns set as an extra defensive layer, but this is not blocking for v1.
- **Suggestion:** The `except Exception: pass` in `models.py` swallows all exceptions during the ALTER TABLE. Narrowing to `sqlite3.OperationalError` would be slightly more precise and would let unexpected errors surface. Not blocking.

### Verdict

Approved

---

## Improvement Notes

<!-- ENGINEER AGENT (second pass): Fill in this section only if the Reviewer set verdict to "Changes Required".
- Address every blocking issue listed in Review Feedback.
- Note which suggestions you acted on and which you deferred (with reason).
- Re-run tests and confirm they pass.
- When done, set current-role to "reviewer" for a second review, or "done" if the reviewer approved inline.
-->

_(Engineer agent fills this in on second pass — leave blank on first pass)_

---

## Final Status

**Outcome**: Added a Kanban board view to the todo app. A new `status` field (`todo`, `in_progress`, `done`) was added to the DB and API, kept in sync with the existing `completed` flag. The frontend gained a List/Board view toggle; the Board view renders three columns with move buttons on each card. All 25 backend tests pass.

**PR**: _TBD — GitHub PR creation is a future step. See docs/NOTES.md > Future Requirements._
