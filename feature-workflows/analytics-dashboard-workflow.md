---
feature: "analytics-dashboard"
requester: "github-issue-6"
status: "completed"
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

# Feature Request: Analytics Dashboard

## Summary

Users want a simple analytics view that shows statistics about their todo activity — how many items
are completed vs. active, completion trends over time, and other useful insights.

## Description

Power users want to understand their productivity patterns. An analytics dashboard reads from the
existing todo data and surfaces aggregated metrics: how many todos are completed, active, overdue
(if due dates are available), how many were created or completed per week, and what the average
completion time is.

## Desired Behaviour

- A new "Analytics" tab or screen is accessible from the main UI.
- The dashboard shows (at minimum):
  - Total todos, total completed, total active
  - Completion rate (% of all todos that are done)
  - Todos created in the last 7 days
  - Todos completed in the last 7 days
- The data is read-only — no editing from this view.
- Data is fetched from a new read-only API endpoint that returns aggregated statistics.
- The UI uses a simple chart or visual representation (e.g. a progress bar or simple bar chart)
  for at least one metric.

## Implementation Complexity Notes

This feature involves:
- One or more new read-only API endpoints that run aggregation queries on the SQLite DB
- A new frontend component for the dashboard view
- Date arithmetic on `created_at` (SQLite `datetime()` functions)
- A charting approach — either a simple custom SVG/HTML bar, or a lightweight JS library

## Out of Scope

- Heatmaps or calendar-based productivity views
- Export to CSV or PDF
- Per-tag or per-priority breakdowns (v1 covers total/active/completed only)
- Real-time auto-refresh
- User accounts or multi-user analytics

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

1. As a power user, I want to see a summary of my total, completed, and active todos so that I can quickly understand the overall state of my task list.
2. As a power user, I want to see my completion rate (percentage of todos marked done) so that I can gauge my overall productivity at a glance.
3. As a power user, I want to see how many todos I created and completed in the last 7 days so that I can track my recent activity and momentum.
4. As a power user, I want to view at least one metric in a visual chart or progress representation so that trends are easier to interpret than raw numbers alone.
5. As a power user, I want the analytics view to be accessible from the main navigation so that I can reach it without disrupting my normal task workflow.

### Acceptance Criteria

- [ ] An "Analytics" tab or screen is reachable from the main UI navigation.
- [ ] The dashboard displays: total todos, total completed, total active, and completion rate (% done).
- [ ] The dashboard displays todos created in the last 7 days and todos completed in the last 7 days.
- [ ] At least one metric is rendered using a visual representation (e.g. a progress bar or bar chart).
- [ ] The analytics view is strictly read-only — no todo can be created, edited, or deleted from this screen.
- [ ] All statistics reflect the current state of the user's todo data without requiring a manual page reload (data is loaded when the view is opened).

### Out of Scope

- Heatmaps or calendar-based productivity views
- Export to CSV or PDF
- Per-tag or per-priority metric breakdowns (v1 covers total/active/completed only)
- Real-time auto-refresh or live-updating statistics
- User accounts or multi-user analytics
- Overdue todo tracking (depends on due-date data availability; deferred to a future iteration)

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

None required.

All needed statistics can be queried directly from the existing `todos` table using `completed`, `status`, and `created_at` timestamps.

### API Changes

**1. `GET /api/todos/stats` (or `GET /api/todos/analytics`)**

Add a new read-only endpoint under the todos blueprint: `GET /api/todos/stats`

**Behavior:**
- Runs aggregation queries against the `todos` table in SQLite using `get_db()`.
- Calculates total todos, total completed, total active, completion rate percentage, todos created in the last 7 days, and todos completed in the last 7 days.
- In SQLite, the 7-day window can be evaluated using date filters against `created_at` (e.g. `created_at >= datetime('now', '-7 days')`).
- For "todos completed in the last 7 days", since there is no dedicated `completed_at` timestamp in v1 schema, it should count todos that are currently completed (`completed = 1`) and were created within the last 7 days (`created_at >= datetime('now', '-7 days')`).

**Response Shape (200 OK):**
```json
{
  "total": 10,
  "completed": 6,
  "active": 4,
  "completion_rate": 60.0,
  "created_last_7_days": 5,
  "completed_last_7_days": 3
}
```

**Notes on values:**
- `total`: integer count of all todos.
- `completed`: integer count of todos where `completed = 1`.
- `active`: integer count of todos where `completed = 0` (or `status != 'done'`).
- `completion_rate`: float between 0.0 and 100.0 (rounded to 1 decimal place, or integer 0 when `total` is 0 to avoid division by zero).
- `created_last_7_days`: integer count of todos with `created_at >= datetime('now', '-7 days')`.
- `completed_last_7_days`: integer count of completed todos created in the last 7 days (`completed = 1 AND created_at >= datetime('now', '-7 days')`).

### Frontend Changes

**1. `todo-app/frontend/src/api.js`**
- Export a new API client function `getStats()` (or `getAnalytics()`) that performs a GET request to `/api/todos/stats`.

**2. `todo-app/frontend/src/components/AnalyticsDashboard.jsx` (New Component)**
- Create a new read-only component `AnalyticsDashboard` that receives or fetches statistics and displays:
  - Metric summary cards/tiles: Total Todos, Completed, Active, Created in last 7 days, Completed in last 7 days.
  - Completion Rate visual representation: A styled progress bar (using Tailwind CSS `w-[...%]`, `bg-blue-600` / `bg-green-500` and `bg-gray-200` track) showing the percentage complete, along with the percentage label.
  - Read-only presentation: no edit, delete, or create controls rendered on this view.

**3. `todo-app/frontend/src/components/ViewToggle.jsx`**
- Update the toggle options array to include `'analytics'` in addition to `'list'` and `'board'`.
- Format button label for `'analytics'` as "Analytics" (or keep capitalized `v`).

**4. `todo-app/frontend/src/App.jsx`**
- Extend the `view` state options to support `'analytics'`.
- Fetch stats when switching to the analytics view (or load whenever `view === 'analytics'` or whenever todos change) so data reflects the latest state without manual reload.
- Conditionally render `AnalyticsDashboard` when `view === 'analytics'`, hiding the `AddTodo` input and todo list/kanban board.

### Engineer Checklist

1. **Backend Endpoint (`todo-app/backend/routes.py`)**:
   - Add the `GET /api/todos/stats` route handler to `todos_bp`.
   - Implement the SQL aggregation queries for total, completed, active, created_last_7_days, and completed_last_7_days.
   - Handle the edge case where `total == 0` (return `completion_rate: 0.0` rather than dividing by zero).
   - Ensure the endpoint returns JSON with status code 200.

2. **Backend Tests (`todo-app/backend/tests/test_routes.py`)**:
   - Add a test class `TestGetStats` covering:
     - Empty database returns all zeros (`total: 0, completed: 0, active: 0, completion_rate: 0.0, created_last_7_days: 0, completed_last_7_days: 0`).
     - Correct totals and completion rate calculation with mixed active and completed items.
     - 7-day window filtering for recent items.

3. **Frontend API Client (`todo-app/frontend/src/api.js`)**:
   - Add and export `getStats` calling `GET /api/todos/stats`.

4. **Frontend UI Components (`todo-app/frontend/src/components/`)**:
   - Create `AnalyticsDashboard.jsx` displaying the required metrics and the completion rate progress bar using Tailwind CSS.
   - Update `ViewToggle.jsx` to include the `analytics` view option.
   - Update `App.jsx` to render `AnalyticsDashboard` when `view === 'analytics'` and load stats data when opening the view.

5. **Verification**:
   - Run `uv run pytest` from `todo-app/backend/` and verify all tests pass.

### Open Questions / Risks

- **Completed in last 7 days metric**: Since the database schema does not have a separate `completed_at` timestamp, the calculation for "completed in last 7 days" measures todos created in the last 7 days that are currently marked completed (`completed = 1 AND created_at >= datetime('now', '-7 days')`). This avoids schema migrations while satisfying the acceptance criteria. If historical completion timestamps are needed in a future release, a schema migration adding `completed_at` can be introduced.
- **Route registration order**: Ensure `GET /api/todos/stats` does not collide with `PUT /api/todos/<int:todo_id>` or `DELETE /api/todos/<int:todo_id>`. In Flask with integer type converters (`<int:todo_id>`), `/stats` is treated as a distinct static path, but placing `/stats` before parameterized routes is good practice.

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

- **`todo-app/backend/routes.py`** — Added `GET /api/todos/stats` route handler to `todos_bp`. Placed before the parameterized routes to avoid any path ambiguity with `<int:todo_id>`.
- **`todo-app/frontend/src/api.js`** — Exported `getStats()` calling `GET /api/todos/stats`.
- **`todo-app/frontend/src/components/AnalyticsDashboard.jsx`** *(new)* — Read-only component that receives `stats`, `loading`, and `error` props and renders five metric cards plus a Tailwind CSS progress bar for completion rate.
- **`todo-app/frontend/src/components/ViewToggle.jsx`** — Extended the view options array from `['list', 'board']` to `['list', 'board', 'analytics']`; replaced the inline ternary label with a `LABELS` lookup map.
- **`todo-app/frontend/src/App.jsx`** — Added `stats`, `statsLoading`, and `statsError` state; added a `useEffect` that fires `getStats()` whenever `view === 'analytics'`; conditionally renders `AnalyticsDashboard` when the analytics view is active, hiding `AddTodo` and the list/board content.
- **`todo-app/backend/tests/test_routes.py`** — Added `TestGetStats` test class (6 tests).

### Approach

The backend endpoint runs five lightweight `SELECT COUNT(*)` queries inside a single `get_db()` context, consistent with the existing route style. Division-by-zero for `completion_rate` is guarded with a conditional (`if total > 0 else 0.0`). The `/stats` path is registered before the `<int:todo_id>` parameterised routes; Flask's integer type converter already makes them distinct, but the ordering follows the architect's recommendation as good practice.

The frontend fetches stats lazily — only when the user navigates to the analytics view — via a `useEffect` dependent on `[view]`. This avoids unnecessary API calls while keeping the data fresh each time the view is opened, satisfying the acceptance criterion that data reflects the current state without a manual page reload.

`AnalyticsDashboard` is a stateless presentational component: all state (stats, loading, error) lives in `App.jsx` and is passed down as props, matching the existing pattern used by `TodoList` and `KanbanBoard`.

### Tests Added

`TestGetStats` in `todo-app/backend/tests/test_routes.py` — 6 tests:

1. `test_empty_db_returns_all_zeros` — verifies all fields are 0 / 0.0 on an empty DB.
2. `test_correct_totals_and_completion_rate` — 2 active + 1 completed → checks total, completed, active, and `completion_rate`.
3. `test_all_completed_gives_100_percent` — all todos completed → `completion_rate == 100.0`.
4. `test_recently_created_todos_counted` — todos just created via the API appear in `created_last_7_days`.
5. `test_completed_last_7_days_counts_completed_recent_todos` — 1 recent done + 1 recent active → `completed_last_7_days == 1`.
6. `test_old_todos_not_counted_in_7_day_window` — a todo inserted with `created_at = '2000-01-01'` does not appear in either 7-day count.

All 37 tests pass (`uv run pytest -v` from `todo-app/backend/`).

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

None

### Suggestions

1. **Query Optimization (Backend)**: The five separate `COUNT(*)` queries in `get_stats()` ([`todo-app/backend/routes.py:46-59`](todo-app/backend/routes.py:46)) could optionally be collapsed into a single SQL statement using conditional aggregation (e.g. `SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END)`). Given the expected dataset size in SQLite, the current approach is clean, readable, and completely sufficient.
2. **Progress Bar Accessibility (Frontend)**: In [`todo-app/frontend/src/components/AnalyticsDashboard.jsx:48-52`](todo-app/frontend/src/components/AnalyticsDashboard.jsx:48), consider adding ARIA attributes (`role="progressbar"`, `aria-valuenow={completion_rate}`, `aria-valuemin="0"`, `aria-valuemax="100"`) to enhance screen-reader support.

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

<!-- ALL AGENTS: This section is filled in last, once the reviewer approves.
- Summarise what was built.
- Note the PR reference once GitHub integration is available.
-->

**Outcome**: Successfully implemented the Analytics Dashboard feature across backend and frontend. Added `GET /api/todos/stats` endpoint returning aggregated metrics (total, completed, active, completion rate, created in last 7 days, completed in last 7 days) with division-by-zero protection. Implemented frontend `AnalyticsDashboard` component with KPI summary cards and completion rate progress bar, updated navigation toggle in `ViewToggle`, integrated lazy data-fetching and error handling in `App.jsx`, and validated test suite with 6 new unit tests.

**PR**: _TBD — GitHub PR creation is a future step. See docs/NOTES.md > Future Requirements._
