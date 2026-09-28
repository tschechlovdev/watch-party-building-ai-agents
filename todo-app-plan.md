# Todo App — Implementation Plan

## Overview

Build a full-stack todo application from scratch with:
- **Backend**: Python Flask REST API with SQLite (via the built-in `sqlite3` module)
- **Frontend**: React (Vite) with Tailwind CSS
- **Features**: Create, read, update (title + completion toggle), delete todos; in-place title editing
- **No auth, no external DB server required**

All code lives under a new `todo-app/` directory in the workspace root.

---

## Sub-Tasks

---

### Sub-Task 1 — Backend: Project scaffold & database layer

**Status**: [x] done

**Intent**
Set up the Flask project structure and implement the SQLite database layer. This is the foundation everything else builds on.

**Expected Outcomes**
- `todo-app/backend/` directory exists with all required files
- Running `flask run` starts the server without errors
- SQLite database file (`todos.db`) is auto-created on first run
- `todos` table is created with the correct schema

**Todo List**
1. Create `todo-app/backend/` directory
2. Create `requirements.txt` with pinned versions: `flask`, `flask-cors`
3. Create `models.py`:
   - `get_db()` helper that opens/returns a SQLite connection with `row_factory = sqlite3.Row`
   - `init_db()` that creates the `todos` table if it does not exist
4. Create `app.py`:
   - Initialize Flask app
   - Configure CORS (allow `http://localhost:5173` — Vite dev server)
   - Call `init_db()` on startup
   - Register blueprint/routes (stub — routes implemented in Sub-Task 2)
5. Verify `flask run` starts cleanly and `todos.db` is created

**Relevant Context**
- Use Python's built-in `sqlite3` — no ORM needed
- `flask-cors` is required so the Vite dev server (port 5173) can call Flask (port 5000)
- Bind Flask to `127.0.0.1` only (security rule: no `0.0.0.0` binding)

**Database Schema**
```sql
CREATE TABLE IF NOT EXISTS todos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT   NOT NULL DEFAULT (datetime('now'))
);
```

---

### Sub-Task 2 — Backend: REST API routes

**Status**: [x] done

**Intent**
Implement the four CRUD endpoints. All responses use JSON; all inputs are validated minimally (title must be non-empty string).

**Expected Outcomes**
- `GET    /api/todos`        → 200 with array of all todos (newest first)
- `POST   /api/todos`        → 201 with created todo; 400 if title missing/empty
- `PUT    /api/todos/<id>`   → 200 with updated todo; 400 on bad input; 404 if not found
- `DELETE /api/todos/<id>`   → 204 No Content; 404 if not found
- All error responses return `{"error": "<message>"}` — no stack traces exposed to client

**Todo List**
1. Implement `GET /api/todos` — query all rows ordered by `created_at DESC`, serialize to list of dicts
2. Implement `POST /api/todos` — read `title` from JSON body, insert row, return full created row
3. Implement `PUT /api/todos/<id>` — accept `title` and/or `completed` fields, update only provided fields, return updated row
4. Implement `DELETE /api/todos/<id>` — delete row, return 204
5. Add a helper `todo_to_dict(row)` to convert `sqlite3.Row` → plain dict
6. Add generic 404 handler returning `{"error": "Not found"}`
7. Manually test all four endpoints with `curl` or a REST client

**Relevant Context**
- Builds directly on `models.py` and `app.py` from Sub-Task 1
- `completed` is stored as INTEGER (0/1) in SQLite; serialize as boolean in JSON responses
- Never return raw exception messages to the client (security rule)

---

### Sub-Task 3 — Frontend: Project scaffold & Tailwind setup

**Status**: [x] done

**Intent**
Scaffold the React + Vite project and configure Tailwind CSS and the dev-server proxy so API calls to `/api/*` are forwarded to Flask without CORS issues during development.

**Expected Outcomes**
- `todo-app/frontend/` scaffolded via `npm create vite@latest`
- Tailwind CSS installed and working (utility classes apply styles)
- `vite.config.js` proxy routes `/api` → `http://127.0.0.1:5000`
- `npm run dev` starts without errors and shows default Vite page

**Todo List**
1. Scaffold with `npm create vite@latest frontend -- --template react` inside `todo-app/`
2. Install Tailwind: `npm install -D tailwindcss @tailwindcss/vite`
3. Add Tailwind Vite plugin to `vite.config.js`
4. Add `@import "tailwindcss"` to `src/index.css`
5. Add proxy to `vite.config.js`:
   ```js
   server: { proxy: { '/api': 'http://127.0.0.1:5000' } }
   ```
6. Remove Vite boilerplate from `App.jsx` and `index.css` (keep only Tailwind import)
7. Verify `npm run dev` runs and Tailwind classes work on a test element

**Relevant Context**
- Tailwind v4 uses the Vite plugin approach (`@tailwindcss/vite`) — no `tailwind.config.js` needed
- The Vite proxy eliminates the need for hardcoded `http://localhost:5000` in fetch calls

---

### Sub-Task 4 — Frontend: API client module

**Status**: [x] done

**Intent**
Centralise all backend communication in a single `api.js` module so components never contain raw `fetch` calls. This keeps components clean and makes the API surface easy to change.

**Expected Outcomes**
- `src/api.js` exports four async functions: `getTodos`, `createTodo`, `updateTodo`, `deleteTodo`
- All functions throw a descriptive `Error` on non-2xx responses
- No hardcoded URLs — all calls go to relative `/api/todos` paths (resolved by the Vite proxy)

**Todo List**
1. Create `src/api.js` with a shared `request(path, options)` helper that checks `response.ok` and throws on errors
2. Implement `getTodos()` → `GET /api/todos`
3. Implement `createTodo(title)` → `POST /api/todos`
4. Implement `updateTodo(id, fields)` → `PUT /api/todos/:id` (fields: `{ title?, completed? }`)
5. Implement `deleteTodo(id)` → `DELETE /api/todos/:id`

**Relevant Context**
- Used by `App.jsx` in Sub-Task 5
- Relative paths work because of the Vite proxy configured in Sub-Task 3

---

### Sub-Task 5 — Frontend: React components & App wiring

**Status**: [x] done

**Intent**
Build the three UI components and wire them together in `App.jsx` with local state. All data mutations go through the `api.js` module.

**Expected Outcomes**
- `AddTodo` — text input + submit button; calls `createTodo`, clears input on success
- `TodoItem` — displays title and completion checkbox; clicking title activates an inline `<input>` for editing; blur or Enter saves; Escape cancels; delete button calls `deleteTodo`
- `TodoList` — renders a list of `TodoItem` components; handles empty-state message
- `App.jsx` — fetches todos on mount, holds the `todos` array in state, passes callbacks down; all state updates are optimistic-free (re-fetch or local splice after confirmed API response)
- Full CRUD flow works end-to-end in the browser

**Todo List**
1. Create `src/components/AddTodo.jsx` — controlled input, calls `onAdd(title)` prop, disables submit on empty input
2. Create `src/components/TodoItem.jsx`:
   - `isEditing` local state; toggled by clicking the title text
   - On save: call `onUpdate(id, { title: newTitle })` then exit edit mode
   - Escape key resets input to original title and exits edit mode
   - Checkbox `onChange` calls `onUpdate(id, { completed: !todo.completed })`
   - Delete button calls `onDelete(id)`
3. Create `src/components/TodoList.jsx` — maps `todos` array to `TodoItem`; shows "No todos yet." when empty
4. Wire `App.jsx`:
   - `useEffect` to call `getTodos()` on mount and populate state
   - `handleAdd`, `handleUpdate`, `handleDelete` callbacks that call `api.js` functions then update local state
5. Style all components with Tailwind utility classes (clean, readable — no external component library)

**Relevant Context**
- Builds on `api.js` from Sub-Task 4
- Keep state management in `App.jsx` only — no prop drilling beyond one level, no external state library needed for this scope

---

## Technology Stack Summary

| Layer | Choice | Reason |
|---|---|---|
| Backend framework | Flask | Lightweight, minimal boilerplate for a simple API |
| Database | SQLite via `sqlite3` | Zero installation, file-based, sufficient for this scope |
| CORS | flask-cors | Single-line setup for dev cross-origin support |
| Frontend framework | React 19 + Vite | Fast dev server, modern defaults |
| Styling | Tailwind CSS v4 | Utility-first, no design system overhead |
| API communication | Native `fetch` | No extra dependencies needed |
