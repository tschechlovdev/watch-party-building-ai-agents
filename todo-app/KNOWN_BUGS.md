# Known Bugs (intentionally injected)

This document describes three bugs that were deliberately introduced into the
todo app as test fixtures for the agentic SDLC workflow (e.g. for exercising the
Reviewer and Engineer agents). Each entry lists the symptom, the root cause, why
it is easy to miss, and the fix.

The bugs are independent. Each one can be reproduced and fixed on its own, and
none of them changes the symptoms of another.

> The existing backend test suite (`todo-app/backend/tests/test_routes.py`)
> passes with all three bugs present. None of the bugs is covered by a test.

| # | Summary | Files |
|---|---|---|
| 1 | A todo cannot be marked incomplete | `backend/routes.py` |
| 2 | Creating a todo returns the wrong record | `backend/routes.py` |
| 3 | Deleting a todo does not remove it from the UI (frontend) | `frontend/src/App.jsx` |

---

## Bug 1 — A todo cannot be marked incomplete

| | |
|---|---|
| **Layer** | Backend |
| **File** | [`backend/routes.py`](backend/routes.py:61) (`update_todo`) |

### Symptom
- Checking a todo works. Unchecking it does not: the checkbox snaps back to
  checked, the strikethrough stays, and the "X / Y completed" counter does not
  decrease.
- No error is shown. The API returns `200 OK`.
- Reloading the page shows the todo still completed, so the data was never
  changed.

### Root cause
The handler used to check whether the `completed` key was present in the request
body. It now checks whether the value is truthy:

```python
completed = data.get("completed")
if completed:
    fields["completed"] = 1
```

A request of `{"completed": false}` is falsy, so the field is never added to the
`UPDATE`. The handler then returns the unchanged row, and the frontend replaces
its local copy with that stale row.

### Why it is easy to miss
- The code reads like an ordinary `.get()` idiom.
- The frontend and the API contract are both correct, and the response looks
  successful.
- No test sets `completed` to `false`.

### Fix
Test for the key (or `is not None`) and store the actual value:

```python
if "completed" in data:
    fields["completed"] = 1 if data["completed"] else 0
```

### Suggested regression test
`PUT /api/todos/<id>` with `{"completed": true}` and then `{"completed": false}`
must return `completed: false` on the second call.

---

## Bug 2 — Creating a todo returns the wrong record

| | |
|---|---|
| **Layer** | Backend (database access) |
| **File** | [`backend/routes.py`](backend/routes.py:38) (`create_todo`) |

### Symptom
- The first todo added to an empty list looks fine.
- From the second todo onward, the new item shown in the UI is a copy of todo #1
  (its title and state), not what was typed.
- React warns about duplicate `key` values, because two list items share an id.
- Edit and delete actions on the new item act on todo #1, because the UI is using
  that id.
- After a page reload the list is correct, because the new row was saved
  properly. This makes the bug look intermittent.
- If todo #1 has been deleted, the lookup returns `None`,
  `todo_to_dict(None)` raises `TypeError`, the API returns `500`, and the UI shows
  "Failed to add todo."

### Root cause
After the `INSERT`, the handler reads the new row back using
`cursor.rowcount` instead of `cursor.lastrowid`:

```python
row = conn.execute(
    "SELECT * FROM todos WHERE id = ?", (cursor.rowcount,)
).fetchone()
```

`rowcount` is the number of rows affected, which is always `1` for a single
insert. It is not the id of the new row.

### Why it is easy to miss
- Both attributes live on the same cursor, so the mix-up is easy to make.
- It gives the correct result when the table is empty (the new row has id 1).
- The existing tests only check a single post, or check the list afterwards.

### Fix
Use `cursor.lastrowid`:

```python
"SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)
```

### Suggested regression test
Create two todos and assert that the second `POST` response has the second
todo's title and a different `id` from the first.

---

## Bug 3 — Deleting a todo does not remove it from the UI

| | |
|---|---|
| **Layer** | Frontend |
| **File** | [`frontend/src/App.jsx`](frontend/src/App.jsx:34) (`handleDelete`) |

### Symptom
- Clicking the delete button on a todo sends a `204` request, but the todo remains
  visible in the list and the "X / Y completed" counter does not update.
- Clicking delete a second time on the same item fails with `404 Not Found`,
  triggering the error banner: `"Failed to delete todo."`
- Adding a new todo, typing into an input, or reloading the page causes the deleted
  todo to disappear, confirming that the backend successfully deleted the record.

### Root cause
The state updater mutates the previous state array in place using `prev.splice(index, 1)`
and returns the same array reference `prev`:

```js
setTodos((prev) => {
  const index = prev.findIndex((t) => t.id === id)
  if (index !== -1) {
    prev.splice(index, 1)
  }
  return prev
})
```

Because the returned array reference is identical to the previous state
(`Object.is(prevState, nextState)` is `true`), React bails out of re-rendering
the component tree.

### Why it is easy to miss
- `array.splice(index, 1)` is idiomatic JavaScript for deleting an element at an index.
- The array in memory is indeed modified, and the backend returns `204 No Content`.
- A debugger inspecting `todos` or a page refresh shows the item was removed.
- It fails purely because React relies on state immutability / reference changes to trigger re-renders.

### Fix
Return a new array reference (e.g. using `filter`):

```js
setTodos((prev) => prev.filter((t) => t.id !== id))
```

### Suggested regression test
A frontend test that renders a todo list, simulates clicking delete on one item,
and asserts that the item is immediately removed from the DOM without requiring a
page reload or unrelated state update.

---

## Reverting

| Bug | Revert |
|---|---|
| 1 | Restore the `"completed" in data` check in `update_todo`. |
| 2 | Change `cursor.rowcount` back to `cursor.lastrowid` in `create_todo`. |
| 3 | Restore `setTodos((prev) => prev.filter((t) => t.id !== id))` in `handleDelete`. |
