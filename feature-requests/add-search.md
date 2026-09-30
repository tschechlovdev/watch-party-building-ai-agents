# Feature Request: Search & Filter

## Summary

Allow users to search todos by title keyword and filter by completion status.

## Motivation

As the todo list grows it becomes hard to find specific items.
A simple text search and a status filter would cover the vast majority of lookup needs.

## Proposed Behaviour

- A search input above the list filters displayed todos to those whose title contains the typed text (case-insensitive).
- A filter control lets the user show: **All** (default) | **Active** (not completed) | **Completed**.
- Search and filter compose — both can be active at the same time.
- Filtering and searching happen client-side on the already-loaded list (no new API endpoint needed).
- Clearing the search input restores the full list instantly.

## Acceptance Criteria

1. Typing in the search box immediately narrows the visible todo list to title matches.
2. The filter control switches between All / Active / Completed views.
3. Search + filter combine correctly (e.g. "Active" filter + "milk" search shows only active todos containing "milk").
4. An empty result state shows a friendly "No matching todos." message.
5. No backend changes are required — this is a pure frontend feature.
6. All existing backend tests continue to pass.

## Out of Scope

- Server-side search or pagination.
- Search across fields other than title.
- Saved filters.
