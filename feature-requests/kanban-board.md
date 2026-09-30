# Feature Request: Kanban Board

## Summary

Add a Kanban board view that organises todos into swim-lane columns by status.

## Motivation

A flat list works for simple task tracking but becomes hard to manage as items grow.
A Kanban board lets users see work-in-progress limits and move cards between stages visually.

## Proposed Behaviour

- A new **Board** view toggle switches the main layout from list to Kanban.
- Three default columns: **To Do**, **In Progress**, **Done**.
- Each todo card lives in the column that matches its status.
- Users can drag a card from one column to another; the backend status is updated on drop.
- The existing list view remains accessible via a view toggle button.

## Acceptance Criteria

1. A `status` field is added to todos: `"todo"` | `"in_progress"` | `"done"`. Default is `"todo"`.
2. `POST /api/todos` accepts an optional `status` field.
3. `PUT /api/todos/<id>` accepts `status` to move a card between columns.
4. `GET /api/todos` returns `status` on every item.
5. The frontend renders three columns with the correct cards in each.
6. Dragging a card to another column updates its status via `PUT /api/todos/<id>`.
7. The `completed` boolean stays in sync: `status: "done"` sets `completed: true`; moving back sets it `false`.
8. The list view still works unchanged.
9. All existing backend tests continue to pass.

## Out of Scope

- Custom column names or additional columns.
- WIP limits.
- Card ordering within a column.
- Persistence of column order.
