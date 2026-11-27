---
feature: "Search and Filter"
slug: "add-search"
feature-request-file: "feature-requests/add-search.md"
current-role: done
needs-architect: false
branch: "feature/add-search"
---

# Feature Workflow: Search and Filter

## PM Analysis

_Filled in by the PM Agent._

**Architect phase:** Not needed (`needs-architect: false`). This is a pure client-side frontend
change: no DB schema change (the `todos` table already has `title` and `completed`), no new API
endpoints, and no new frontend architecture beyond local UI state and a filtered view of the
existing `todos` array in `App.jsx` / `TodoList.jsx`.

### User Stories

1. As a user with many todos, I want to type in a search bar and see the list narrow to matching titles as I type, so that I can find a specific item without scrolling.
2. As a user, I want to toggle between All, Active, and Completed todos, so that I can focus on what is still to do or review what I have finished.
3. As a user, I want search and the status filter to work together, so that I can, for example, find only the completed todos that contain "report".
4. As a user, I want the count below the list and an empty-result message to reflect what I am currently seeing, so that I always know how many items match and when nothing does.

### Acceptance Criteria

1. A search text input is shown at the top of the todo list in the List view, above the list. It has an accessible label (e.g. `aria-label="Search todos"`) and placeholder text.
2. Typing in the search input filters the visible todos in real time (on every change, no submit button or debounce delay required).
3. Matching is case-insensitive substring matching against the todo `title` only (e.g. "GRO" matches "Buy groceries"). Leading/trailing whitespace in the search term is ignored.
4. A filter toggle offers three options: **All**, **Active** (`completed` is false), and **Completed** (`completed` is true). **All** is selected by default, and the selected option is visually indicated and exposes `aria-pressed` (consistent with the existing List/Board toggle).
5. Search and filter are combined (logical AND): only todos that match the search term and the selected filter are displayed.
6. Clearing the search input (empty string) restores the full list, still subject to the currently selected filter.
7. The completed-count text below the list (currently `{completed} / {total} completed`) is computed from the filtered result set, not from all todos.
8. When todos exist but none match the current search and filter, the list shows the message "No matching todos." When there are no todos at all, the existing "No todos yet. Add one above!" message is still shown.
9. Search and filtering are performed entirely client-side on the already-loaded `todos` state. No new API endpoints or API calls are added, and no backend files are changed.
10. Adding, updating (e.g. toggling completed), and deleting todos continue to work while a search/filter is active. Results update accordingly (e.g. a todo marked completed disappears from the Active filter), and the search term and filter selection are preserved.
11. The search input and filter toggle are shown in the List view only. The Board view behaves as it does today.
12. All existing backend tests continue to pass (`cd todo-app/backend && uv run pytest`).

### Out of Scope

- Server-side or full-text search.
- Searching across tags, due dates, priority, status, or any field other than `title` (title-only for v1).
- Saved searches or named filters.
- Sorting controls.
- Applying search or the Active/Completed filter to the Board (Kanban) view.
- Persisting search/filter state across page reloads (e.g. URL params or localStorage).
- Search term highlighting, debounce, or fuzzy matching.
- Any backend, API, or database change.

### Branch

`feature/add-search` (existing branch; no new branch was created by the PM Agent).

---

## Architecture Design

_Filled in by the Architect Agent._

### DB Schema Changes

<!-- New tables, columns, or migrations required. None if no schema change. -->

### API Changes

<!-- New or modified endpoints with request/response shapes. -->

### Frontend Changes

<!-- Components, state, and UX changes required. -->

### Engineer Checklist

<!-- Ordered step-by-step checklist for the Engineer to follow. -->

---

## Implementation Notes

_Filled in by the Engineer Agent._

### Changes Made

- `todo-app/frontend/src/components/TodoFilters.jsx` (new): search input (`aria-label="Search todos"`, placeholder) and All / Active / Completed toggle with `aria-pressed`, styled like the List/Board toggle.
- `todo-app/frontend/src/App.jsx`: added `search` and `filter` state; `filteredTodos` = case-insensitive substring match on the trimmed title AND the status filter; renders `TodoFilters` + `TodoList` (with `filteredTodos`) in List view only; the `N / M completed` count uses the filtered list in List view and all todos in Board view (Board unchanged).
- `todo-app/frontend/src/components/TodoList.jsx`: new `totalCount` prop; shows "No matching todos." when todos exist but none match, otherwise keeps "No todos yet. Add one above!".
- No backend changes.

### Tests

No new tests: this is a pure frontend change and the frontend has no test framework (project convention for frontend-only changes is `npm run lint && npm run build`). No backend behaviour changed; the existing backend suite was re-run and passes.

### Test Run Result

Frontend (`cd todo-app/frontend && npm run lint && npm run build`):

```
> frontend@0.0.0 lint
> oxlint

Found 0 warnings and 0 errors.
Finished in 11ms on 10 files with 104 rules using 14 threads.

> frontend@0.0.0 build
> vite build

vite v8.3.1 building client environment for production...
transforming...
✓ 23 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-BYUYNA-D.css   14.00 kB │ gzip:  3.64 kB
dist/assets/index-B-0m4xob.js   227.10 kB │ gzip: 70.91 kB

✓ built in 200ms
```

Backend (`cd todo-app/backend && uv run pytest`):

```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/dennistreder-tschechlov/workspace/watchparty-building-ai-agents-01-12-26/my-agent-team-search/todo-app/backend
configfile: pyproject.toml
testpaths: tests
collected 39 items

tests/test_routes.py .......................................             [100%]

============================== 39 passed in 0.40s ==============================
```

---

## Review Feedback

_Filled in by the Reviewer Agent._

### Issues Found

None.

Criteria checked against `App.jsx`, `components/TodoList.jsx` and `components/TodoFilters.jsx`:

1. AC#1 met. `TodoFilters` renders the search input with `aria-label="Search todos"` and a placeholder, above `TodoList` in the List view.
2. AC#2 met. `onChange` calls `setSearch` on every keystroke, with no debounce or submit.
3. AC#3 met. `t.title.toLowerCase().includes(search.trim().toLowerCase())` is case-insensitive, title-only, and ignores surrounding whitespace.
4. AC#4 met. All/Active/Completed buttons with `aria-pressed`, the same styling as the List/Board toggle, and `'all'` as the default.
5. AC#5 met. Search and status filter are combined with `&&` in `filteredTodos`.
6. AC#6 met. An empty term matches every title (`includes('')`), so the status filter still applies.
7. AC#7 met. In List view the count uses `filteredTodos`. In Board view it uses all todos, so the Board is unchanged.
8. AC#8 met. `TodoList` shows "No matching todos." when `totalCount > 0` and the filtered list is empty. Otherwise it shows "No todos yet. Add one above!".
9. AC#9 met. Filtering is a client-side derivation of `todos`. There are no new API calls and no backend changes.
10. AC#10 met. `search` and `filter` state is separate from `todos`. Add, update and delete handlers only change `todos`, and `filteredTodos` is recomputed on each render, so results update and the search and filter stay put.
11. AC#11 met. `TodoFilters` is rendered only in the `view === 'list'` branch. `KanbanBoard` still receives all `todos`.
12. AC#12 met per the Engineer's Test Run Result (39 backend tests passed). No backend files were changed. I did not re-run the tests because the reviewer role may not run shell commands.

Non-blocking notes:
- The filtering logic is a few lines inline in `App.jsx`, so the diff stays small. This is acceptable.
- There are no automated frontend tests. The Engineer's notes say the frontend has no test framework, and lint and build pass.
- Security: the search term is only used for client-side string comparison. React escapes rendered output, so there is no injection concern.

### Verdict

Approved

---

## Outcome

Approved: Search and Filter (search input plus All/Active/Completed toggle, List view only, client-side) meets all 12 acceptance criteria on branch `feature/add-search`.
