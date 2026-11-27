---
feature: "Due Dates"
slug: "add-due-dates"
feature-request-file: "feature-requests/add-due-dates.md"
current-role: done
needs-architect: true
branch: "feature/add-due-dates"
---

# Feature Workflow: Due Dates

## PM Analysis

_Filled in by the PM Agent._

### User Stories

1. As a todo-list user, I want to optionally set a due date (date only) when creating or editing a todo, so that I can attach a real-world deadline to the task without tracking it elsewhere.
2. As a todo-list user, I want to see a todo's due date in a human-readable format (e.g. "Due Jun 15"), so that I can see my deadlines at a glance.
3. As a todo-list user, I want overdue todos and todos due today to be visually highlighted with distinct styles, so that I can immediately tell which items need attention.
4. As a todo-list user, I want to filter my list by all, overdue, due today, or no due date, so that I can focus on the todos that matter right now.
5. As an existing user, I want todos without a due date to behave exactly as they do today, so that adopting the feature does not disrupt my current data or workflow.

### Acceptance Criteria

1. **Persistence:** Each todo has an optional `due_date` (date only, ISO `YYYY-MM-DD` string, or `null`). It is persisted in the database; existing todos and existing databases are migrated so that they have `due_date = null` and continue to work without data loss.
2. **API – create:** `POST /api/todos` accepts an optional `due_date`. Omitted or `null` results in `due_date: null`. A valid date is stored and returned.
3. **API – update:** `PUT /api/todos/<id>` accepts `due_date`. A valid `YYYY-MM-DD` string sets it; `null` clears it; omitting the field leaves it unchanged (partial updates of other fields such as `title`, `status`, `completed` do not alter `due_date`).
4. **API – validation:** An invalid `due_date` (non-string, wrong format, or a non-existent calendar date such as `2025-02-30`) is rejected with HTTP 400 and a JSON `{"error": "..."}` body, on both create and update. An empty string is rejected or treated as `null` consistently (Architect to decide and document).
5. **API – read:** `GET /api/todos` and all todo responses include a `due_date` field (string or `null`) for every todo.
6. **Create UI:** The add-todo form has an optional date input. Submitting with a date creates a todo with that due date; submitting without one creates a todo with no due date. The input resets after submission.
7. **Edit UI:** A user can set, change, and clear a todo's due date from the todo item in the list view; the change is persisted via the API and reflected immediately in the UI.
8. **Display:** A todo with a due date shows it in a human-readable format such as "Due Jun 15". A todo without a due date shows no due-date text. Due-date display is also present on Kanban board cards.
9. **Overdue highlight:** If `due_date` is before today (browser's local date) and the todo is not completed (`completed` false / status not `done`), it is visually highlighted as overdue (e.g. red text or badge).
10. **Due-today highlight:** If `due_date` equals today (local date) and the todo is not completed, it is highlighted in a visually distinct style from overdue (e.g. amber/yellow).
11. **Completed todos:** Completed todos with a due date show the date but are not highlighted as overdue or due today.
12. **Filter:** The list view provides a filter with options All, Overdue, Due today, and No due date. All shows every todo; Overdue shows only non-completed todos with a past due date; Due today shows only non-completed todos due today; No due date shows only todos with `due_date = null`. The default is All.
13. **Filter + counts:** Applying a filter does not delete or alter any data, and an empty filtered result shows an empty list without errors. The existing "X / Y completed" footer continues to work.
14. **Backwards compatibility:** Existing behaviours (create, rename, toggle complete, status change via Kanban drag-and-drop, delete) continue to work unchanged for todos with and without due dates.
15. **Tests:** Backend pytest tests cover creating/updating/clearing `due_date`, invalid values returning 400, `due_date` being present in list responses, and the DB migration for existing databases; `cd todo-app/backend && uv run pytest` passes.

### Out of Scope

- Due time (time-of-day); date only for v1
- Recurring todos (e.g. "every Monday")
- Calendar view
- Email or push notifications for upcoming due dates
- Server-side sorting by due date (client-side sort is acceptable but not required for v1)
- Server-side filtering (filtering is done client-side in v1)
- Time-zone handling beyond using the browser's local date for "today"
- Filter persistence across page reloads
- Bulk editing of due dates

### Branch

feature/add-due-dates

---

## Architecture Design

_Filled in by the Architect Agent._

> Note: the backend uses plain `sqlite3` (no SQLAlchemy). Schema and migration live in `init_db()` in `todo-app/backend/models.py`; migration follows the existing `PRAGMA table_info` + `ALTER TABLE` pattern used for `status`.

### DB Schema Changes

- New column on `todos`: `due_date TEXT NULL` (no default → `NULL`). Stores an ISO `YYYY-MM-DD` string or `NULL`.
- Fresh DBs: add `due_date TEXT` to the `CREATE TABLE IF NOT EXISTS todos (...)` statement in `init_db()`.
- Existing DBs (idempotent migration), in `init_db()` after the existing `status` migration:
  ```python
  if "due_date" not in columns:
      conn.execute("ALTER TABLE todos ADD COLUMN due_date TEXT")
  ```
  `columns` is computed once before the `status` migration; since the `status` migration does not remove/rename columns, the same list is valid. Existing rows get `due_date = NULL`; no data loss. Calling `init_db()` repeatedly must be a no-op.
- No index (filtering is client-side in v1).

### API Changes

**Decision (open question — empty string):** an empty string `""` for `due_date` is **rejected with HTTP 400** (same as any other malformed value), on both create and update. Rationale: matches the strict handling already used for `status` (`""` is rejected there), keeps one unambiguous way to express "no date" (`null`), and avoids silently coercing input. The frontend must send `null` (never `""`) to clear a date, and omit/`null` on create when no date is chosen.

**Validation helper (routes.py):**
- Add `DUE_DATE_ERROR = "due_date must be a valid date in YYYY-MM-DD format or null"`.
- Add `_invalid_due_date(data)`: returns `False` if `"due_date"` not in `data` or `data["due_date"] is None`; otherwise returns `True` unless the value is a `str` that (a) matches `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)` (strict zero-padded format; do NOT rely on `date.fromisoformat` alone, as it accepts other ISO forms on Python 3.11+, and do NOT use `\d`, which matches non-ASCII digits) **and** parses via `datetime.date.fromisoformat(value)` / `datetime.strptime(value, "%Y-%m-%d")` without `ValueError` (rejects `2025-02-30`). Non-strings (numbers, bools, lists, objects) and `""` are invalid.
- `todo_to_dict` adds `"due_date": row["due_date"]` (string or `None`).

**`GET /api/todos`** — unchanged request. Each todo object now includes `"due_date": "YYYY-MM-DD" | null`. Response shape: `{id, title, completed, status, created_at, due_date}`. Order unchanged (`created_at DESC, id DESC`).

**`POST /api/todos`**
- Body: `title` (string, required — unchanged), `status` (optional — unchanged), **`due_date`** (optional; string `YYYY-MM-DD` or `null`; omitted ⇒ `null`).
- Validation order: title → status → due_date; first failure returns 400.
- INSERT becomes `INSERT INTO todos (title, status, completed, due_date) VALUES (?, ?, ?, ?)` with `data.get("due_date")` (omitted → `None`).
- Success: `201` with the full todo including `due_date`.
- Errors: `400 {"error": "title is required"}`, `400 {"error": STATUS_ERROR}`, `400 {"error": DUE_DATE_ERROR}` (non-string, `""`, wrong format, impossible date). Nothing is inserted on error.

**`PUT /api/todos/<id>`**
- Body (all optional, partial update): `title`, `status`, `completed` (unchanged), **`due_date`** (string `YYYY-MM-DD` sets; `null` clears; key absent ⇒ unchanged).
- After the existing 404 check and title/status validation, validate due_date: if `_invalid_due_date(data)` → `400 {"error": DUE_DATE_ERROR}` before any write. If `"due_date" in data`, add `fields["due_date"] = data["due_date"]` (may be `None`, which writes `NULL`).
- Updates to `title`/`status`/`completed` must not touch `due_date`; an empty payload still changes nothing.
- Success: `200` with full todo including `due_date`.
- Errors: `404 {"error": "Not found"}` (unchanged, takes precedence for unknown id), `400` as above.

**`DELETE /api/todos/<id>`** — unchanged.

### Frontend Changes

Stack: React + Tailwind (utility classes; no CSS file changes needed). Filtering and "today" logic are client-side only.

**New file `todo-app/frontend/src/dueDate.js`** (pure helpers, no React):
- `todayLocal()` → local-date string `YYYY-MM-DD` built from `new Date()` via `getFullYear()/getMonth()/getDate()` (zero-padded). Do **not** use `toISOString()` (UTC shift).
- `formatDue(dueDate)` → e.g. `"Due Jun 15"`. Parse the string manually (`const [y, m, d] = dueDate.split('-').map(Number); new Date(y, m - 1, d)`) to avoid UTC parsing shifts, then `toLocaleDateString(undefined, { month: 'short', day: 'numeric' })`; prefix with `"Due "`.
- `getDueState(todo, today)` → `'overdue'` if `todo.due_date && !todo.completed && todo.due_date < today`; `'today'` if `todo.due_date === today && !todo.completed`; otherwise `null`. (ISO date strings compare correctly lexicographically.) Completed todos always return `null`.
- `DUE_FILTERS` = `[{key:'all',label:'All'},{key:'overdue',label:'Overdue'},{key:'today',label:'Due today'},{key:'none',label:'No due date'}]`.
- `matchesFilter(todo, filter, today)` → `all`: true; `overdue`: `getDueState === 'overdue'`; `today`: `getDueState === 'today'`; `none`: `todo.due_date == null`.
- `dueClasses(state)` → Tailwind classes: overdue `text-red-600 font-medium`; today `text-amber-600 font-medium`; null `text-gray-500`.

**`api.js`**: `createTodo(title, dueDate)` sends `{ title, ...(dueDate ? { due_date: dueDate } : {}) }`. `updateTodo` unchanged (callers pass `{ due_date: 'YYYY-MM-DD' }` or `{ due_date: null }`).

**`App.jsx`**:
- `handleAdd(title, dueDate)` → `createTodo(title, dueDate)`.
- New state `const [filter, setFilter] = useState('all')` (not persisted).
- Compute `today = todayLocal()` per render and `visibleTodos = todos.filter((t) => matchesFilter(t, filter, today))`.
- When `view === 'list'`: render a filter control (row of buttons styled like the existing List/Board toggle, `aria-pressed`, labels from `DUE_FILTERS`) above the list, and pass `visibleTodos` plus `isFiltered={filter !== 'all'}` to `TodoList`. Kanban board keeps receiving the unfiltered `todos` (filter is a list-view feature).
- The "X / Y completed" footer keeps using the full `todos` array (unchanged).

**`AddTodo.jsx`**:
- Add state `dueDate` (`''`), and an optional `<input type="date" aria-label="Due date">` next to the title input (bound to `dueDate`).
- `onAdd(trimmed, dueDate || null)`; after submit reset both `title` and `dueDate` to `''`. Submit button disabled logic stays based on title only.

**`TodoList.jsx`**: accept optional `isFiltered` prop. If `todos.length === 0`: show `"No todos match this filter."` when `isFiltered`, else existing "No todos yet. Add one above!". No errors on empty filtered result.

**`TodoItem.jsx`**:
- Compute `const dueState = getDueState(todo, todayLocal())`.
- Show due text when `todo.due_date` is set: `<span className={dueClasses(dueState)}>{formatDue(todo.due_date)}</span>` (small text, placed after the title); no text when `due_date` is null. For overdue/today optionally also tint the `<li>` border (`border-red-300` / `border-amber-300`) for a clearer highlight.
- Edit control: an `<input type="date" aria-label="Edit due date" value={todo.due_date ?? ''}>` whose `onChange={(e) => onUpdate(todo.id, { due_date: e.target.value || null })}` (empty value → `null`, never `""`), plus a small "Clear due date" `×` button (`aria-label="Clear due date"`) rendered only when `todo.due_date` is set, calling `onUpdate(todo.id, { due_date: null })`. UI updates immediately via the existing `handleUpdate` → `setTodos` flow (server response replaces the item).
- Existing title edit / checkbox / delete behaviour unchanged.

**`KanbanCard.jsx`**: show the same read-only due text below/after the title when `todo.due_date` is set, with highlight from `getDueState(todo, todayLocal())` (use `todo.completed`, which the backend keeps in sync with `status === 'done'`). No date editing on cards required. Drag-and-drop unchanged (still sends only `{ status }`, so `due_date` is untouched).

**State management summary**: new `filter` state in `App`, new `dueDate` state in `AddTodo`; `todos` items gain a `due_date` field. No new API endpoints.

### Engineer Checklist

1. In `/Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/backend/models.py`, add `due_date TEXT` to the `CREATE TABLE IF NOT EXISTS todos` statement in `init_db()`.
2. In the same `init_db()`, after the `status` migration block (before `conn.commit()`), add: `if "due_date" not in columns: conn.execute("ALTER TABLE todos ADD COLUMN due_date TEXT")`.
3. In `/Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/backend/routes.py`, add `import re` and `from datetime import date`, plus the constant `DUE_DATE_ERROR = "due_date must be a valid date in YYYY-MM-DD format or null"`.
4. Add `_invalid_due_date(data)` per the API spec (absent or `None` ⇒ valid; must be `str`, match `[0-9]{4}-[0-9]{2}-[0-9]{2}` via `re.fullmatch`, and parse with `date.fromisoformat` without `ValueError`; `""` is invalid).
5. Add `"due_date": row["due_date"]` to `todo_to_dict`.
6. In `create_todo`, after the status check, return `400 {"error": DUE_DATE_ERROR}` if `_invalid_due_date(data)`; change the INSERT to include `due_date` (`data.get("due_date")`) as the 4th column/value.
7. In `update_todo`, after the status validation, return `400 {"error": DUE_DATE_ERROR}` if `_invalid_due_date(data)`; then, if `"due_date" in data`, set `fields["due_date"] = data["due_date"]` (`None` clears). Do not touch `due_date` when the key is absent.
8. In `/Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/backend/tests/test_routes.py`, add backend tests (new classes, matching existing style):
   - create without `due_date` → `due_date is None`; create with `"2025-06-15"` → stored and returned; create with explicit `null` → `None`.
   - `GET /api/todos` includes the `due_date` key on every item (mix of with/without).
   - update: set a date; change a date; clear with `null`; omitted `due_date` preserved across `title`, `status`, `completed` updates and an empty payload.
   - invalid values on create and update → 400 with `"error"` and no change/insert (parametrize: `"2025-02-30"`, `"15-06-2025"`, `"2025-6-15"`, `"20250615"`, `"not-a-date"`, `""`, `123`, `True`, `["2025-06-15"]`).
   - unknown id with `due_date` on PUT → 404.
   - migration: build a legacy DB lacking both `status` and `due_date` (and one with `status` but no `due_date`), run `models.init_db()` twice (idempotent), assert rows retained with `due_date is None` via `GET /api/todos`.
9. Create `/Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/frontend/src/dueDate.js` with `todayLocal`, `formatDue`, `getDueState`, `DUE_FILTERS`, `matchesFilter`, `dueClasses` as specified above.
10. In `/Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/frontend/src/api.js`, change `createTodo` to `(title, dueDate)` and include `due_date` only when truthy.
11. In `.../todo-app/frontend/src/components/AddTodo.jsx`, add `dueDate` state, a `<input type="date" aria-label="Due date">`, call `onAdd(trimmed, dueDate || null)`, and reset `dueDate` to `''` after submit.
12. In `.../todo-app/frontend/src/App.jsx`, update `handleAdd(title, dueDate)`, add `filter` state, compute `visibleTodos`, render the filter button row in list view only, pass `visibleTodos` and `isFiltered` to `TodoList`; leave the Kanban `todos` prop and the footer count based on the full `todos`.
13. In `.../todo-app/frontend/src/components/TodoList.jsx`, accept `isFiltered` and show "No todos match this filter." for an empty filtered result.
14. In `.../todo-app/frontend/src/components/TodoItem.jsx`, add the formatted/highlighted due text, the date input (empty → `null`), and the clear button, per spec; completed todos are never highlighted.
15. In `.../todo-app/frontend/src/components/KanbanCard.jsx`, add the read-only due text with the same overdue/today highlighting (none when completed).
16. Run `cd /Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/frontend && npm run build` (if dependencies are installed) to confirm the frontend compiles.
17. Run `cd todo-app/backend && uv run pytest` and confirm all tests pass.

---

## Implementation Notes

_Filled in by the Engineer Agent._

### Changes Made

- `todo-app/backend/models.py`: added nullable `due_date TEXT` to `CREATE TABLE` and an idempotent `ALTER TABLE` migration for existing databases.
- `todo-app/backend/routes.py`: `todo_to_dict` returns `due_date`; new `_invalid_due_date` (strict `YYYY-MM-DD`, real calendar date, `null` allowed, `""` rejected) and `DUE_DATE_ERROR`; POST stores `due_date`; PUT sets/clears it and leaves it unchanged when the key is absent; invalid values return 400.
- `todo-app/frontend/src/dueDate.js` (new): helpers `todayLocal`, `formatDue`, `getDueState`, `DUE_FILTERS`, `matchesFilter`, `dueClasses`.
- `todo-app/frontend/src/api.js`: `createTodo(title, dueDate)` sends `due_date` only when set.
- `todo-app/frontend/src/components/AddTodo.jsx`: optional date input, reset after submit.
- `todo-app/frontend/src/App.jsx`: `filter` state, filter button row in list view, `visibleTodos` passed to `TodoList`; Kanban and "X / Y completed" footer still use all todos.
- `todo-app/frontend/src/components/TodoList.jsx`: "No todos match this filter." empty state.
- `todo-app/frontend/src/components/TodoItem.jsx`: "Due Jun 15" text with overdue (red) / today (amber) highlight, date input to set/change, clear button; completed todos are not highlighted.
- `todo-app/frontend/src/components/KanbanCard.jsx`: read-only due text with the same highlighting.
- `feature-requests/add-due-dates.md`: replaced with the text of GitHub issue #5 (done during intake).

Frontend: `npm install`, `npm run lint` (0 warnings, 0 errors) and `npm run build` succeed.

### Tests

`todo-app/backend/tests/test_routes.py`: added `TestDueDateOnCreateAndGet` (default null, explicit null, set, present in list, invalid values → 400 and nothing inserted), `TestDueDateOnUpdate` (set, change, clear with null, preserved when omitted across title/status/completed/empty payloads, invalid values → 400 and unchanged, unknown id → 404) and `TestDueDateMigration` (legacy DB without `status` and `due_date`, DB with `status` only; `init_db()` run twice; rows retained with `due_date` null).

### Test Run Result

```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-due-dates/todo-app/backend
configfile: pyproject.toml
testpaths: tests
collected 72 items

tests/test_routes.py ................................................... [ 70%]
.....................                                                    [100%]

============================== 72 passed in 0.23s ==============================
```

---

## Review Feedback

_Filled in by the Reviewer Agent._

### Issues Found

None

Reviewed (by reading source, per the reviewer skill's no-shell rule; test/lint/build results are taken from the Engineer's recorded run: 72 passed, lint and build clean):

- AC#1 (persistence/migration): `due_date TEXT` is in `CREATE TABLE` and added by an idempotent `PRAGMA table_info` + `ALTER TABLE` migration in `models.py`. Existing rows get NULL.
- AC#2–5 (API): `routes.py` returns `due_date` from `todo_to_dict`. `_invalid_due_date` uses a strict ASCII `[0-9]{4}-[0-9]{2}-[0-9]{2}` full match plus `date.fromisoformat`, so it rejects non-strings, `""`, wrong formats and impossible dates like `2025-02-30`. POST stores it, and PUT sets it, clears it with null, or leaves it alone when the key is absent. Validation runs before any write, and 404 still takes precedence for an unknown id.
- AC#6 (create UI): `AddTodo.jsx` has an optional date input, sends `null` when empty, and resets after submit. `api.js` only includes `due_date` when it is set.
- AC#7 (edit UI): `TodoItem.jsx` has a date input (empty → `null`, never `""`) and a clear button. Changes go through the existing `handleUpdate` flow.
- AC#8–11 (display/highlight): `formatDue` parses the date manually (no UTC shift) and `todayLocal` uses local date parts. `getDueState` returns null for completed todos. Overdue is red and due-today is amber. `KanbanCard.jsx` shows the due text.
- AC#12–13 (filter): All, Overdue, Due today and No due date filters are client-side, with All as the default. The empty state is "No todos match this filter.". Kanban and the "X / Y completed" footer still use the full `todos`.
- AC#14 (compatibility): Title edit, checkbox, delete and Kanban drag-and-drop are untouched. Drag-and-drop still sends only `{ status }`.
- AC#15 (tests): `TestDueDateOnCreateAndGet`, `TestDueDateOnUpdate` and `TestDueDateMigration` cover create, update, clear, preserve, invalid values (create and update), the list response, 404, and migration of legacy DBs run twice.

Minor non-blocking note: "No due date" filter semantics (`due_date == null`) include completed todos, which matches AC#12.

### Verdict

Approved

---

## Outcome

Approved: all 15 acceptance criteria are met and the workflow is complete.
