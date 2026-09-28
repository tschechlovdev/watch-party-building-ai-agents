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
