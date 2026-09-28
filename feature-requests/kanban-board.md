# Feature Request: Kanban Board

## Summary

Users want a Kanban-style board view so they can visualise their todos as cards moving through
defined stages (e.g. To Do → In Progress → Done).

## Description

The current list view is fine for simple task tracking but doesn't support workflow-oriented work
where tasks have meaningful stages. A Kanban board groups todos into columns representing stages,
and users can move cards between columns by dragging or using a control.

## Desired Behaviour

- The UI offers a toggle between the existing list view and a new board view.
- The board view displays three columns: **To Do**, **In Progress**, **Done**.
- Each todo belongs to exactly one column based on its status.
- Users can move a todo to a different column (changing its status).
- Todos that are marked "completed" are automatically moved to (or reflected in) the Done column.
- The existing list view continues to work unchanged.
- A new `status` field is added to todos: `todo`, `in_progress`, or `done`.
- `done` status corresponds to `completed = true`; the two are kept in sync.

## Implementation Complexity Notes

This feature involves:
- A new `status` column in the DB (or a mapping from `completed` to `todo`/`done`)
- New API support for updating `status`
- A significant new frontend component (the board layout and column logic)
- Optional: drag-and-drop (can be deferred to v2; use a "Move to..." button for v1)

## Out of Scope

- Custom column names or adding more than three columns (v1 uses fixed columns)
- Swimlanes, labels, or story-point estimates on cards
- Drag-and-drop (v1 uses a move button; DnD is a v2 enhancement)
- Card comments or attachments
- WIP limits
