# Feature Request: Analytics Dashboard

## Summary

Add a simple analytics dashboard that shows aggregate statistics about the user's todos.

## Motivation

Users have no visibility into their productivity or backlog health.
A lightweight stats page would surface completion rates, overdue counts, and priority distribution
without requiring any external reporting tool.

## Proposed Behaviour

- A new **Dashboard** link in the top navigation opens a dedicated stats page.
- The page shows:
  - Total todos, completed count, and completion percentage.
  - Active (incomplete) todos broken down by priority (if the Priorities feature is present).
  - Number of overdue todos (if the Due Dates feature is present; otherwise omit).
  - A simple bar or donut chart visualising completion status.
- Stats are fetched from a new `/api/stats` endpoint.
- The dashboard is read-only — no editing from this view.

## Acceptance Criteria

1. `GET /api/stats` returns `{ total, completed, active, overdue }` (overdue is 0 if due dates are not implemented).
2. The frontend renders the stats as clearly labelled cards or chart elements.
3. Navigating to the dashboard and back to the list preserves the list state.
4. All existing backend tests continue to pass; new tests cover the `/api/stats` endpoint.

## Out of Scope

- Historical trends or time-series charts.
- Per-user analytics.
- Export to CSV or PDF.
- Real-time auto-refresh.
