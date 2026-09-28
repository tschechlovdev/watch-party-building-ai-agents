# Feature Request: Tags and Labels

## Summary

Users want to tag their todos with one or more free-form labels so they can group and filter related
items across different projects or contexts.

## Description

A single todo list quickly becomes overwhelming when it mixes work tasks, personal errands, and
project-specific items. Tags let users attach one or more short labels (e.g. "work", "shopping",
"urgent", "project-alpha") to each todo and then filter the list by tag to see only relevant items.

## Desired Behaviour

- A todo can have zero or more tags.
- Tags are free-form short text strings (e.g. "work", "home", "#sprint-3").
- When creating or editing a todo, the user can add or remove tags.
- The list view shows tags as small chips/badges on each todo item.
- Users can click a tag to filter the list and show only todos with that tag.
- The same tag name used on multiple todos represents the same tag (case-insensitive).

## Out of Scope

- Tag colours or icons
- Hierarchical tags (parent / child)
- Bulk-tagging multiple todos at once
- Tag suggestions or autocomplete (nice to have for v2)
- Tag management screen (rename, delete all uses of a tag)
