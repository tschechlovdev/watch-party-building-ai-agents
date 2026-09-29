---
feature: "Search and Filter"
requester: "watch-party"
status: "complete"
current-role: "done"
needs-architect: false
---

# Feature Workflow

---

## Feature Request

# Feature Request: Search and Filter

## Summary

Users want to search and filter their todo list so they can quickly find specific items without
scrolling through everything.

## Description

As the number of todos grows, finding a specific item or group of items becomes tedious. A search
bar and filter controls let users instantly narrow the visible list to what they need.

## Desired Behaviour

- A search bar at the top of the list filters todos in real time as the user types.
- Search matches against the todo title (case-insensitive, substring match).
- Search is performed client-side — no new API endpoints required.
- A filter toggle lets users show: All todos, Active only (not completed), Completed only.
- Search and filter work together — applying a filter while searching shows only matching,
  filtered results.
- The count displayed below the list reflects the filtered result set, not the total.
- When the search term is cleared, the full list (subject to active filter) reappears.

## Out of Scope

- Full-text search on the server side
- Search across tags, due dates, or priority fields (title-only for v1)
- Saved searches or named filters
- Sorting controls

---

## PM Analysis

### User Stories

1. As a user with a growing todo list, I want to type in a search bar and see matching todos instantly so that I can find a specific item without scrolling through everything.
2. As a user, I want to filter my list to show only active (incomplete) todos so that I can focus on what still needs to be done.
3. As a user, I want to filter my list to show only completed todos so that I can review what I have already finished.
4. As a user, I want search and filter to work together so that I can, for example, find all completed todos matching a keyword.
5. As a user, I want the item count to reflect how many todos are currently visible (after search/filter) so that I always know how many results I am looking at.

### Acceptance Criteria

- [ ] A search input is visible above the todo list; typing into it narrows the displayed todos in real time (no page reload or API call).
- [ ] Search is case-insensitive and matches any substring of the todo title.
- [ ] Three filter options are available: **All**, **Active** (not completed), **Completed**; exactly one is active at a time; **All** is the default.
- [ ] Search and filter are applied together — the list shows only todos that satisfy both the active filter and the current search term.
- [ ] Clearing the search input (or deleting all typed characters) restores the full list subject to the active filter.
- [ ] The item count shown below the list reflects the number of currently visible (filtered + searched) todos, not the total number of todos.

### Out of Scope

- Server-side or full-text search (no new API endpoints)
- Search across any field other than title (no due date, priority, or tag search in v1)
- Saved or named filters
- Sorting controls of any kind

### Architect Recommendation

Needs Architect: **No** — this feature is entirely client-side. No DB schema changes, no new or modified API endpoints, and no significant state management restructuring are required. The engineer only needs to add a search input and filter toggle to App.jsx, derive a filteredTodos array from the existing todos state, and pass that derived array to TodoList. Plain English is sufficient to guide the engineer without a formal architecture phase.

---

## Architecture Design

_(Skipped — needs-architect: false)_

---

## Implementation Notes

### Files Changed

- `todo-app/frontend/src/App.jsx` — added `searchTerm` and `filter` state; added `filteredTodos` derived via `useMemo`; rendered the new `SearchFilter` component; updated `TodoList` to receive `filteredTodos`; updated the item count line to reflect `filteredTodos.length`
- `todo-app/frontend/src/components/SearchFilter.jsx` — new component with a search input (`type="search"`) and three filter buttons (All / Active / Completed) that report changes back via `onSearchChange` and `onFilterChange` props

### Approach

The feature is implemented entirely in the React client with no backend changes. `App.jsx` holds `searchTerm` (string) and `filter` ('All' | 'Active' | 'Completed') as state. A `useMemo` hook derives `filteredTodos` from the full `todos` array by applying both the active filter and a case-insensitive substring match on `title`. The new `SearchFilter` component is a pure presentational component — it receives its values as props and emits changes upward, keeping all state in `App.jsx` consistent with the existing pattern. The existing 17 backend tests all still pass unchanged.

### Tests Added

This is a frontend-only feature with no new backend logic. The existing 17 backend tests cover all API behaviour and pass without modification (`uv run pytest` — 17 passed, 0 failed).

Frontend unit tests for `filteredTodos` logic were not added because the project has no frontend test setup (no Vitest/Jest configuration). The filtering logic is a single, straightforward `Array.filter` expression that is directly validated by the acceptance criteria during manual testing.

---

## Review Feedback

### Blocking Issues

None.

All six acceptance criteria are satisfied:
- Search input renders above the list and filters in real time via `useMemo` over local state (no API calls).
- Case-insensitive substring match is correctly implemented: `t.title.toLowerCase().includes(term)` where `term = searchTerm.trim().toLowerCase()`.
- Three filter buttons (All / Active / Completed) with `All` as default; `aria-pressed` correctly reflects active state; only one can be active at a time.
- Combined logic uses `&&` — both `matchesFilter` and `matchesSearch` must be true.
- Clearing the search term sets `term = ''` making `matchesSearch` always `true`, restoring the filtered list.
- Item count uses `filteredTodos.length` and `filteredTodos.filter(t => t.completed).length` — not the raw `todos` array.

No backend changes, no security issues, no hardcoded secrets, no 0.0.0.0 binding.

### Suggestions

Suggestion: `TodoList.jsx` currently shows "No todos yet. Add one above!" when `todos.length === 0`. This message is also shown when todos exist but are all filtered/searched out (i.e. `filteredTodos.length === 0` but `todos.length > 0`). Consider differentiating the empty state: e.g. "No todos match your search." when a search term or non-All filter is active. This is a UX improvement and is not required for the acceptance criteria to pass.

### Verdict

Approved

---

## Improvement Notes

_(Engineer agent fills this in on second pass — leave blank on first pass)_

---

## Final Status

**Outcome**: Implemented client-side search and filter for the todo list. A new `SearchFilter` component provides a real-time search input and All/Active/Completed filter toggle. The `filteredTodos` derived value is computed via `useMemo` in `App.jsx` and passed down to `TodoList` and the item count. No backend changes were required. All 17 existing backend tests pass.

**PR**: _TBD — GitHub PR creation is a future step._
