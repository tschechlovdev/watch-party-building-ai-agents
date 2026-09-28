# Feature Request: Due Dates

## Summary

Users want to assign a due date to each todo so they can track deadlines and see at a glance which
items are overdue.

## Description

Many tasks have a real-world deadline. Without due dates, users must keep track of deadlines
externally (in a calendar, in their head, etc.) while managing their todo list separately. Adding a
due date field lets users attach a target completion date to each todo and highlights overdue items.

## Desired Behaviour

- When creating or editing a todo, the user can optionally set a due date (date only, no time).
- Todos without a due date behave exactly as today.
- Todos with a due date display the date in a human-readable format (e.g. "Due Jun 15").
- If the due date is in the past and the todo is not completed, the item is visually highlighted
  as overdue (e.g. red text or a warning badge).
- If the due date is today, it is highlighted differently from overdue (e.g. amber/yellow).
- The list can be filtered to show: all todos, overdue only, due today, or no due date.

## Out of Scope

- Due time (time-of-day — date only for v1)
- Recurring todos (e.g. "every Monday")
- Calendar view
- Email or push notifications for upcoming due dates
- Sorting by due date on the server side (client-side sort is acceptable for v1)
