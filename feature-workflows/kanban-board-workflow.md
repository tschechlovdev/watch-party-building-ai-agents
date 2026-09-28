---
feature: "kanban-board"
requester: "watch-party"
status: "complete"
current-role: "done"
---

# Feature Workflow

<!-- INSTRUCTIONS FOR ALL AGENTS
This document is the shared memory for one feature request moving through the Agentic SDLC workflow.
Each agent role reads the sections above their own, then appends their section below.
Do not modify sections written by a previous agent.
Update the `current-role` front matter field to reflect the next role when you finish your section.
Hint comments (like this one) are guidance only — they are not part of your output.
-->

---

## Feature Request

<!-- PM AGENT: Copy the content of the feature request file here verbatim, then begin your analysis below. -->

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

<!-- PM AGENT: Fill in this section.
- Write 3–5 user stories in the format: "As a [user], I want to [action] so that [benefit]."
- List 3–6 acceptance criteria as checkboxes.
- List anything explicitly out of scope.
- Do NOT propose any technical approach — focus on what the user needs, not how to build it.
- When done, set current-role to "architect" in the front matter.
-->

### User Stories

- As a user, I want to switch between a list view and a board view so that I can choose the most useful way to see my todos depending on the type of work I am doing.
- As a user, I want to see my todos grouped into three columns — To Do, In Progress, and Done — so that I can visualise how my work is progressing at a glance.
- As a user, I want to move a todo from one column to another so that I can update its stage as I work through my tasks.
- As a user, I want todos I mark as completed to automatically appear in the Done column so that my board and my list view stay consistent with each other.
- As a user, I want the existing list view to continue working exactly as before so that switching to the board view does not break my current workflow.

### Acceptance Criteria

- [ ] The UI has a visible toggle control (e.g. "List" / "Board" buttons or tabs) that switches between the list view and the board view.
- [ ] The board view displays exactly three columns with the headings: **To Do**, **In Progress**, and **Done**.
- [ ] Each todo appears in exactly one column, determined by its current status (`todo` → To Do, `in_progress` → In Progress, `done` → Done).
- [ ] Each todo card in the board view has controls to move it to an adjacent or any other column; moving a card updates its status immediately and persists across page refresh.
- [ ] When a todo is marked as completed (via the existing checkbox in list view), its status becomes `done` and it appears in the Done column in board view. Conversely, moving a card to Done marks it as completed.
- [ ] The existing list view — including creating, editing, completing, and deleting todos — continues to work exactly as it did before this feature was added.

### Out of Scope

- Custom column names or a configurable number of columns (v1 uses three fixed columns only)
- Drag-and-drop reordering of cards (v1 uses explicit move controls; drag-and-drop is a v2 enhancement)
- Swimlanes, story-point estimates, or labels on board cards
- Card comments, attachments, or expanded card detail views
- WIP (Work In Progress) limits per column

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

Add a `status` column to the `todos` table:

```
ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'
Valid values: 'todo', 'in_progress', 'done'
```

Update `init_db()` in `models.py` to include `status` in the `CREATE TABLE IF NOT EXISTS` statement so fresh databases get the column. For existing databases the `ALTER TABLE` is not needed at startup — SQLite's `CREATE TABLE IF NOT EXISTS` only runs on first creation. The engineer must handle the case where the column already exists if the app is used against a pre-existing `todos.db` (see Open Questions).

**Sync rule** (enforced by the API, not the DB):
- When `status` is set to `done` → also set `completed = 1`
- When `status` is set to `todo` or `in_progress` → also set `completed = 0`
- When `completed` is set to `true` → also set `status = 'done'`
- When `completed` is set to `false` → also set `status = 'todo'` (unless status is already `in_progress`, in which case keep `in_progress`)

### API Changes

**1. `GET /api/todos` — add `status` to the response**

The `todo_to_dict` serializer must include the new `status` field:
```
{ "id": 1, "title": "...", "completed": false, "status": "todo", "created_at": "..." }
```
No request changes. Existing consumers that ignore unknown fields are unaffected.

**2. `POST /api/todos` — accept optional `status` in request body**

- If `status` is provided, validate it is one of `todo`, `in_progress`, `done`. Return 400 if invalid.
- If `status` is omitted, default to `'todo'`.
- Apply sync rule: if `status` is `done`, set `completed = 1`; otherwise `completed = 0`.

**3. `PUT /api/todos/<id>` — accept `status` updates and enforce sync**

- If `status` is provided in the request body, validate it is one of `todo`, `in_progress`, `done`. Return 400 if invalid.
- Apply the sync rule in both directions:
  - `status` provided → derive and set `completed`
  - `completed` provided (without `status`) → derive and set `status` using the rule above
  - Both provided → `status` takes precedence; re-derive `completed` from `status`

No new endpoints are required.

### Frontend Changes

**1. `api.js` — no changes required**

`updateTodo(id, fields)` already accepts arbitrary fields and passes them through. The frontend will call it with `{ status: 'in_progress' }` or `{ status: 'done' }` etc. No new function needed.

**2. `App.jsx` — add `view` state and a view toggle**

Add a `view` state variable: `'list'` or `'board'` (default `'list'`).
Add a `handleStatusChange(id, newStatus)` handler that calls `updateTodo(id, { status: newStatus })` and updates the local todos state (same pattern as `handleUpdate`).
Pass `view`, `onViewChange` (setter), `todos`, `onUpdate`, `onDelete`, and `onStatusChange` down to the root render area.
Replace the current direct render of `<TodoList>` with a conditional: if `view === 'list'` render `<TodoList>`, else render `<KanbanBoard>`.

**3. New component: `src/components/KanbanBoard.jsx`**

Renders a three-column board layout using Tailwind CSS flex or grid.
Columns (fixed, in this order): **To Do** (`status === 'todo'`), **In Progress** (`status === 'in_progress'`), **Done** (`status === 'done'`).
Each column header shows the column name and a count of cards in that column.
Each card in a column renders the todo title and a set of move buttons — one button per column the card is NOT currently in (e.g. a card in "To Do" shows "→ In Progress" and "→ Done" buttons).
Clicking a move button calls `onStatusChange(todo.id, targetStatus)`.
Cards in the Done column should visually indicate completion (e.g. muted text, similar to the line-through style in `TodoItem`).
Props: `todos` (full array — the component filters by status internally), `onStatusChange`, `onDelete`.
No inline editing in board view (editing remains a list-view-only feature for v1).

**4. New component: `src/components/ViewToggle.jsx`**

A simple two-button toggle: "List" and "Board".
The active view button is visually differentiated (e.g. filled background vs. outline).
Props: `view` (current value), `onViewChange` (callback).
Rendered in `App.jsx` above the `<AddTodo>` input.

### Engineer Checklist

1. Update `init_db()` in `models.py` — add `status TEXT NOT NULL DEFAULT 'todo'` to the `CREATE TABLE IF NOT EXISTS` statement.
2. Add a helper function in `routes.py` to apply the `status`/`completed` sync rule given a `status` value and a `completed` value, returning the resolved `(status, completed)` pair.
3. Update `todo_to_dict` in `routes.py` to include `"status": row["status"]` in the returned dict.
4. Update `create_todo` in `routes.py` to accept and validate optional `status` field; apply sync rule before INSERT.
5. Update `update_todo` in `routes.py` to accept and validate optional `status` field; apply sync rule before UPDATE.
6. Write backend tests in `tests/test_routes.py` covering: create with default status, create with explicit status, update status, update completed (verify status syncs), update with invalid status (400), board-visible status in GET response.
7. Create `src/components/ViewToggle.jsx` with List/Board buttons and `view`/`onViewChange` props.
8. Create `src/components/KanbanBoard.jsx` with three fixed columns, card rendering, and move buttons.
9. Update `App.jsx`: add `view` state (default `'list'`), add `handleStatusChange`, add `<ViewToggle>`, conditionally render `<TodoList>` or `<KanbanBoard>`.
10. Verify existing list-view behaviour is unchanged: create, edit inline, complete via checkbox, delete.
11. Run `uv run pytest` from `todo-app/backend/` and confirm all tests pass.

### Open Questions / Risks

1. **Existing `todos.db`**: `init_db()` uses `CREATE TABLE IF NOT EXISTS`, so it will not add the `status` column to a pre-existing database. The engineer should either (a) delete `todos.db` during development so it is recreated with the new schema, or (b) add a migration step using `ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'` wrapped in a try/except to handle the case where the column already exists. Option (a) is simplest for development; the decision is left to the engineer to document in Implementation Notes.

2. **Sync edge case — "un-completing" a Done card**: When a user moves a card from Done back to In Progress (or To Do) via the board, the `completed` flag must be set to `0`. The sync rule handles this, but the engineer should verify the existing list-view checkbox reflects the change without a page refresh (i.e. the local state update in `handleStatusChange` must update both `status` and `completed` on the todo object in state).

3. **No editing in board view (by design)**: Inline title editing is intentionally list-view only for v1. The board cards should not have the click-to-edit behaviour of `TodoItem`. This is a deliberate out-of-scope decision, not an omission.

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

- `todo-app/backend/models.py` — added `VALID_STATUSES` constant; added `status TEXT NOT NULL DEFAULT 'todo'` to the `CREATE TABLE IF NOT EXISTS` schema; added `ALTER TABLE … ADD COLUMN` with try/except for migration of pre-existing databases
- `todo-app/backend/routes.py` — added `_resolve_status_completed()` sync helper; added `status` field to `todo_to_dict`; updated `create_todo` to accept and validate optional `status`; updated `update_todo` to accept and validate optional `status` and apply bidirectional sync
- `todo-app/backend/tests/test_routes.py` — added `TestStatusField` class (5 tests) and `TestStatusSync` class (8 tests)
- `todo-app/frontend/src/components/ViewToggle.jsx` — new component: List/Board toggle button pair
- `todo-app/frontend/src/components/KanbanBoard.jsx` — new component: three-column board with `KanbanCard` sub-component and move buttons
- `todo-app/frontend/src/App.jsx` — added `view` state (default `'list'`), `handleStatusChange` handler, `<ViewToggle>` in header, conditional render of `<TodoList>` vs `<KanbanBoard>`; widened max container from `max-w-md` to `max-w-2xl` for board layout; `<AddTodo>` hidden in board view

### Approach

The `status` field is stored as a TEXT column in the DB with the `completed` INTEGER kept in sync by the API. The sync logic is centralised in `_resolve_status_completed()` so both `create_todo` and `update_todo` use the same rules. `status` takes precedence when both fields are provided in a single request. The frontend receives `status` in every todo object and uses it to place cards in the correct column. No new API endpoints were needed — `updateTodo(id, { status })` reuses the existing PUT endpoint. The existing `todos.db` migration is handled via `ALTER TABLE … ADD COLUMN` wrapped in a try/except in `init_db()`.

**Open question acknowledged**: The `in_progress` preservation rule (un-completing an `in_progress` todo keeps it in `in_progress` rather than downgrading to `todo`) was implemented as designed; the test `test_update_completed_false_preserves_in_progress` verifies this.

### Tests Added

**`TestStatusField`** (5 tests):
- `test_new_todo_has_default_status_todo` — default status is `todo`, completed is False
- `test_get_returns_status_field` — GET response includes `status` key
- `test_create_with_explicit_status_in_progress` — status stored, completed stays False
- `test_create_with_status_done_sets_completed_true` — status `done` syncs completed to True
- `test_create_with_invalid_status_returns_400` — unknown status value rejected

**`TestStatusSync`** (8 tests):
- `test_update_status_to_done_sets_completed_true`
- `test_update_status_to_in_progress_sets_completed_false`
- `test_update_status_to_todo_sets_completed_false`
- `test_update_completed_true_sets_status_done`
- `test_update_completed_false_from_done_sets_status_todo`
- `test_update_completed_false_preserves_in_progress`
- `test_update_invalid_status_returns_400`
- `test_status_takes_precedence_when_both_provided`

All 30 tests pass (`uv run pytest` — 30 passed in 0.12s).

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

**1. `todo-app/backend/models.py` lines 27–31 — Migration does not backfill existing rows**

`ALTER TABLE todos ADD COLUMN status TEXT NOT NULL DEFAULT 'todo'` in SQLite sets the default for *new* rows only. Rows that existed before the migration have `status = NULL`. The `KanbanBoard` component filters with `t.status === col.key`, so NULL-status todos match no column and are invisible in board view. This is the bug the user observed — even newly created todos were invisible because the Flask dev server was running against an existing `todos.db` that had been created before `status` was added, and the old rows (and possibly cached schema) caused `SELECT *` to return `NULL` for `status`.

**Fix:** Add a backfill `UPDATE` immediately after the `ALTER TABLE` try/except block:

```python
conn.execute(
    "UPDATE todos SET status = CASE WHEN completed = 1 THEN 'done' ELSE 'todo' END"
    " WHERE status IS NULL OR status = ''"
)
```

This must run inside the same `with get_db() as conn:` block, before `conn.commit()`.

**Note:** New todos created *after* the server restarts with the fixed `init_db()` will have `status = 'todo'` correctly — so the fix is purely the missing backfill for pre-existing rows.

---

### Suggestions

**Suggestion 1:** Add a test that verifies `init_db()` correctly sets `status = 'todo'` on a row that was inserted into the DB *before* the status column existed (simulating the migration scenario). This would have caught the backfill gap before it reached manual testing.

**Suggestion 2:** The `update_todo` route builds a SET clause using an f-string (`f"UPDATE todos SET {set_clause} WHERE id = ?"`). While the keys are controlled (never user-supplied), the `# noqa: S608` suppression comment already acknowledges it. Consider replacing with a whitelist of allowed column names and raising a 400/500 if an unexpected key appears — makes the intent explicit rather than relying on the comment.

**Suggestion 3:** In board view, `AddTodo` is hidden but there is no explanatory text telling the user how to add todos. A one-line hint ("Switch to List view to add todos") in the board view would improve usability.

### Second-Pass Verdict

**Blocking issue fully resolved.** The backfill condition was corrected from `WHERE status IS NULL OR status = ''` to `WHERE completed = 1 AND status = 'todo'` — the right condition given that SQLite's `ALTER TABLE ADD COLUMN DEFAULT` fills existing rows with the default value rather than NULL. The `TestMigrationBackfill` test proves this end-to-end. Suggestion 1 and Suggestion 3 were both acted on. Suggestion 2 deferred with reasonable justification.

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

### Blocking Issue Addressed

**Issue:** `models.py` migration backfill — rows inserted before the `status` column existed were getting SQLite's DEFAULT value of `'todo'` applied by `ALTER TABLE ADD COLUMN`, meaning completed todos silently had `status = 'todo'` instead of `'done'`, and were therefore invisible in the To Do column in board view.

**Root cause discovered during fix:** The original backfill condition (`WHERE status IS NULL OR status = ''`) was incorrect — SQLite `ALTER TABLE … ADD COLUMN … DEFAULT 'todo'` fills existing rows with `'todo'`, not `NULL`. The correct condition is `WHERE completed = 1 AND status = 'todo'`, which catches pre-migration completed rows that were incorrectly given the 'todo' default.

**Fix applied:** Changed the backfill UPDATE in `init_db()` to:
```
UPDATE todos SET status = 'done' WHERE completed = 1 AND status = 'todo'
```
Added a comment explaining the SQLite DEFAULT behaviour.

**Test added:** `TestMigrationBackfill.test_pre_migration_rows_are_backfilled_on_init_db` — creates a legacy schema DB without the `status` column, inserts one active and one completed row, runs `init_db()`, and asserts both rows have the correct status after migration.

### Suggestions Addressed

**Suggestion 1 (add migration test):** Acted on — see test above. This test would have caught the backfill gap during the first pass.

**Suggestion 2 (f-string SET clause whitelist):** Deferred. The `fields` dict is built from a hardcoded list of validated inputs (`title`, `status`, `completed`) — no user input reaches the column name. Adding an explicit whitelist would add complexity without changing security posture. The `# noqa: S608` comment already documents the intent.

**Suggestion 3 (board view add-hint):** Acted on — replaced the conditional `{view === 'list' && <AddTodo>}` with a ternary that shows "Switch to List view to add todos" hint text in board view.

All 31 tests pass (`uv run pytest` — 31 passed in 0.10s).

---

## Final Status

<!-- ALL AGENTS: This section is filled in last, once the reviewer approves.
- Summarise what was built.
- Note the PR reference once GitHub integration is available.
-->

**Outcome**: Added a Kanban board view to the Todo app. A List/Board toggle lets users switch between the existing list view and a new three-column board (To Do / In Progress / Done). Todos are placed in columns by a new `status` field, kept in sync with the existing `completed` field by the API. Cards have move buttons to change status. A `init_db()` migration backfills pre-existing databases correctly. 31 backend tests pass.

**PR**: _TBD — GitHub PR creation is a future step. See docs/NOTES.md > Future Requirements._
