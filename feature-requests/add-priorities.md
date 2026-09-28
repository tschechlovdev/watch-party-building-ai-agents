# Feature Request: Todo Priorities

## Summary

Users want to mark each todo with a priority level so they can focus on what matters most first.

## Description

At the moment all todos look the same regardless of urgency. Users have no way to signal which items
are most important. Adding a priority field — low, medium, or high — lets users triage their list
visually and sort or filter by importance.

## Desired Behaviour

- When creating a new todo, the user can optionally set a priority (default: medium).
- The priority of an existing todo can be changed after creation.
- Each todo displays a visual indicator of its priority (e.g. a badge or colour-coded label).
- Users can filter the list to show only todos of a given priority.

## Priority Levels

| Level | Meaning |
|---|---|
| `high` | Urgent — needs attention soon |
| `medium` | Normal priority (default) |
| `low` | Nice to have, no deadline |

## Out of Scope

- Priority-based notifications or reminders
- Custom priority labels beyond the three fixed levels
- Automatic prioritisation by AI
- Priority sorting on the server side (client-side sort is acceptable for v1)
