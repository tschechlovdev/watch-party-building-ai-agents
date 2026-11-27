# Feature Request: Task Priorities

## Summary

Allow users to assign a priority level to each todo item so they can focus on what matters most.

## Motivation

Currently all tasks look the same. Users have no way to signal urgency or importance.
A simple Low / Medium / High priority field would let users sort and visually distinguish tasks.

## Proposed Behaviour

- When creating a todo, the user can optionally pick a priority: **Low**, **Medium**, or **High**. Default is **Medium**.
- Existing todos without a priority are treated as **Medium**.
- The priority is shown as a coloured badge on each todo item.
- The todo list is sorted by priority descending (High first), then by creation date descending within each priority group.

## Acceptance Criteria

1. `POST /api/todos` accepts an optional `priority` field (`"low"`, `"medium"`, `"high"`).
2. `PUT /api/todos/<id>` accepts an optional `priority` field to update it.
3. `GET /api/todos` returns `priority` on every item; missing values default to `"medium"`.
4. The frontend shows a coloured badge: red = High, yellow = Medium, grey = Low.
5. The list is ordered High → Medium → Low, then newest-first within each group.
6. All existing backend tests continue to pass.

## Out of Scope

- Priority-based filtering or search.
- Custom priority labels.
- Priority sorting toggled by the user — sorting is always applied.
