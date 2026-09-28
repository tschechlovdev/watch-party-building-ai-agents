# Feature Request: Search and Filter

## Summary

Users want to search and filter their todo list so they can quickly find specific items without
scrolling through everything.

## Description

As the number of todos grows, finding a specific item or group of items becomes tedious. A search
bar and filter controls let users instantly narrow the visible list to what they need.

## Desired Behaviour

- A search bar at the top of the list filters todos in real time as the user types.
- Search matches against the todo title (case-insensitive, substring match).
- Search is performed client-side — no new API endpoints required.
- A filter toggle lets users show: All todos, Active only (not completed), Completed only.
- Search and filter work together — applying a filter while searching shows only matching,
  filtered results.
- The count displayed below the list reflects the filtered result set, not the total.
- When the search term is cleared, the full list (subject to active filter) reappears.

## Out of Scope

- Full-text search on the server side
- Search across tags, due dates, or priority fields (title-only for v1)
- Saved searches or named filters
- Sorting controls
