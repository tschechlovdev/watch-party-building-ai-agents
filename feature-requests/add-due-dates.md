# Feature Request: Due Dates

## Summary

Allow users to set a due date on each todo item so they can track deadlines.

## Motivation

Users often have tasks that need to be done by a specific date. Without due dates, the app
cannot help them manage time-sensitive work or surface overdue items.

## Proposed Behaviour

- When creating or editing a todo, the user can optionally set a due date (date only, no time).
- Todos with a due date show the date on the item card.
- Todos that are past their due date and not yet completed are visually highlighted (e.g. red text or border).
- Todos without a due date show no date indicator.

## Acceptance Criteria

1. `POST /api/todos` accepts an optional `due_date` field (ISO 8601 date string, e.g. `"2025-12-31"`).
2. `PUT /api/todos/<id>` accepts an optional `due_date` field; passing `null` clears it.
3. `GET /api/todos` returns `due_date` on every item (`null` if not set).
4. The frontend renders the due date on the card when present.
5. Overdue and incomplete todos are highlighted in red.
6. All existing backend tests continue to pass.

## Out of Scope

- Time-of-day due times.
- Recurring tasks.
- Due-date based filtering or sorting.
- Push notifications or reminders.
