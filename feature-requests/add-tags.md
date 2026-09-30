# Feature Request: Tags / Labels

## Summary

Allow users to attach one or more free-form tags to a todo item for flexible categorisation.

## Motivation

Users often group tasks by project, context, or theme (e.g. "work", "home", "urgent").
A tagging system lets them impose their own structure without a rigid category hierarchy.

## Proposed Behaviour

- A todo can have zero or more tags.
- Tags are short free-form strings (e.g. "work", "urgent", "shopping").
- Tags are shown as chips on the todo card.
- When creating or editing a todo, the user can add or remove tags via a text input (comma-separated or chip-style input).
- Clicking a tag filters the list to show only todos that share that tag.

## Acceptance Criteria

1. `POST /api/todos` accepts an optional `tags` array of strings.
2. `PUT /api/todos/<id>` accepts an optional `tags` array; passing an empty array removes all tags.
3. `GET /api/todos` returns a `tags` array on every item (empty array if none).
4. Tags are stored in a separate `tags` table with a many-to-many join to `todos`.
5. The frontend renders tag chips on each card.
6. Clicking a tag chip filters the list to that tag client-side.
7. All existing backend tests continue to pass.

## Out of Scope

- Tag autocomplete or a global tag management UI.
- Multi-tag AND filtering.
- Tag colours.
