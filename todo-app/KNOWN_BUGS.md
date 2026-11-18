# Known Bugs (intentionally injected)

These bugs were deliberately introduced into the todo app as test fixtures for
the agentic SDLC workflow (e.g. for exercising the Reviewer and Engineer agents
and a bug-fixing skill). Each entry lists the symptom, the root cause, why it is
easy to miss, and the fix.

Bugs are grouped as **business-logic** (the app behaves wrongly) or
**technical** (the tooling or tests are wrong), and rated by:

- **Criticality**: impact on users or data (Critical > High > Medium > Low).
- **Complexity**: effort to find and fix (Easy = one-line fix, Medium = needs a
  failing test or reasoning about two places, Hard = intermittent, needs
  reproduction).

| ID | Summary | Type | Criticality | Complexity | Files |
|---|---|---|---|---|---|
| B2 | Creating a todo returns the wrong record | Business | Critical | Easy | `backend/routes.py` |
| B1 | A todo cannot be marked incomplete | Business | High | Easy | `backend/routes.py` |
| B4 | Editing a title resets `completed` to false | Business | High | Medium | `backend/routes.py` |
| T1 | Test fixture does not isolate the database | Technical | High | Medium | `backend/tests/test_routes.py` |
| B6 | No type validation on request fields | Business | Medium | Medium | `backend/routes.py` |
| B3 | Deleting a todo does not remove it from the UI | Business | Medium | Easy | `frontend/src/App.jsx` |
| B5 | New todos appear at the bottom, not the top | Business | Low | Easy | `frontend/src/App.jsx` |
| B7 | Only 5 todos are ever loaded | Business | Critical | Easy | `backend/routes.py` |
| B8 | Long titles are silently cut to 20 characters | Business | High | Easy | `backend/routes.py` |
| B9 | The "completed" counter is always one too high | Business | Medium | Easy | `frontend/src/App.jsx` |
| B10 | Editing a todo wipes its title | Business | Critical | Easy | `backend/routes.py` |

## In plain words (for non-technical readers)

B1 to B10 are bugs in how the app behaves. T1 is a technical bug that shows up
in the tests.

**B1 — A ticked task can never be un-ticked.**
You tick a task by mistake and click the box again to undo it. The box jumps
back to ticked, and a refresh shows it is still done. The app ignores every
request to mark a task as "not done".

**B2 — Adding a task shows the wrong task.**
You type "Buy milk" and press Add, but the list shows a copy of your very first
task instead. After a refresh the list looks right again, so it seems random.
Until then, clicking edit or delete on the new row changes the first task. In
some cases the app shows an error instead. This is the most serious bug,
because you can change or delete the wrong task.

**B3 — Deleted tasks stay on screen.**
You click the delete button, and nothing seems to happen. The task is really
gone, but the screen does not update. Clicking again gives an error, and the
task only disappears after a refresh or after you add something new.

**B7 — Only five tasks are ever shown.**
You add a sixth task and it seems to work. After a refresh, one task is gone
from the list. The app only loads the five newest tasks and hides the rest.
Your data is still saved, but you cannot see or reach it.

**B8 — Long task names get cut off.**
You type a long task name, and after saving it ends in the middle of a word,
after 20 characters. The app does not warn you. It just throws the rest away.

**B9 — The "done" counter is always too high.**
The small text under the list says, for example, "1 / 5 completed" when you
have not finished a single task. It always shows one more finished task than
there really are.

**B10 — Editing a task erases its name.**
You click a task, change its name and press Enter. The task stays in the list,
but its name is gone and only an empty line is left. After a refresh it is
still empty. Editing is effectively impossible, and every edit destroys the
text you had.

**B4 — Editing a task un-ticks it.**
You finish a task and tick it off. Later you fix a typo in its name, and the
tick disappears. The app treats the edited task as not done, so your progress is
lost without any warning.

**B5 — New tasks show up at the bottom.**
When you add a task, it appears at the bottom of the list. When you refresh the
page, it jumps to the top, where it belongs. The screen and the saved data
disagree about the order, which is confusing but harms nothing.

**B6 — The app accepts nonsense input.**
The app expects a task name to be text and "done" to be a yes or no. If
something else is sent, such as a number as a name or the word "false" as a
yes/no answer, it does not complain properly. It either crashes with an
unfriendly error page or does the opposite of what was meant (the word "false"
counts as "done"). Normal users do not see this, because the screen always
sends the right kind of data, but other programs using the app can.

**T1 — The tests mess with real data.**
Tests should run on a throwaway copy of the data, like a practice room. Here
they run on the real data instead. Test runs fill your real list with junk, and
the tests fail more often each time you run them. The app itself works. The
safety net used to check it is broken.

## How the bugs interact

- **T1 hides and exposes other bugs.** With the fixture pointing at the real
  `todos.db`, the suite fails on a clean run and fails more on every later run
  (leftover rows). It also makes B2 visible in tests, because a shared database
  means the new row is no longer id 1. Fix T1 first, then judge the remaining
  failures.
- With T1 fixed, the existing suite still passes with B1 to B9 present. None of
  them is covered by a test. B10 is the exception: it makes
  `test_updates_title` and `test_updates_title_and_completed_together` fail
  (verified), so those two failures point at B10, not at T1.
- Otherwise the bugs are independent and each can be fixed on its own.

---

## Business-logic bugs

### B2 — Creating a todo returns the wrong record

| | |
|---|---|
| **Criticality / Complexity** | Critical / Easy |
| **File** | `backend/routes.py` (`create_todo`) |

**Symptom**
- The first todo added to an empty list looks fine.
- From the second todo onward, the item shown in the UI is a copy of todo #1,
  not what was typed.
- React warns about duplicate `key` values.
- Edit and delete on the new item act on todo #1.
- After a reload the list is correct, which makes the bug look intermittent.
- If todo #1 was deleted, the lookup returns `None`, `todo_to_dict(None)` raises
  `TypeError`, the API returns `500`, and the UI shows "Failed to add todo."

**Root cause**: after the `INSERT`, the row is read back using `cursor.rowcount`
(always `1`) instead of `cursor.lastrowid`.

```python
"SELECT * FROM todos WHERE id = ?", (cursor.rowcount,)
```

**Why it is easy to miss**: both attributes live on the same cursor, and the
result is correct when the table is empty. With an isolated per-test database,
every test sees an empty table, so the suite passes.

**Fix**: use `cursor.lastrowid`.

**Regression test**: create two todos and assert that the second `POST`
response has the second title and a different `id` from the first.

### B1 — A todo cannot be marked incomplete

| | |
|---|---|
| **Criticality / Complexity** | High / Easy |
| **File** | `backend/routes.py` (`update_todo`) |

**Symptom**
- Checking a todo works. Unchecking it does not: the checkbox snaps back, the
  strikethrough stays, and the "X / Y completed" counter does not decrease.
- The API returns `200 OK`, so no error is shown.
- A reload shows the todo still completed.

**Root cause**: the handler tests the value instead of the key.

```python
completed = data.get("completed")
if completed:
    fields["completed"] = 1
```

`{"completed": false}` is falsy, so the field never reaches the `UPDATE`.

**Why it is easy to miss**: it reads like an ordinary `.get()` idiom, the
response looks successful, and no test sets `completed` to `false`.

**Fix**

```python
if "completed" in data:
    fields["completed"] = 1 if data["completed"] else 0
```

**Regression test**: `PUT` with `{"completed": true}` and then
`{"completed": false}` must return `completed: false` the second time.

### B4 — Editing a title resets `completed` to false

| | |
|---|---|
| **Criticality / Complexity** | High / Medium |
| **File** | `backend/routes.py` (`update_todo`) |

**Symptom**
- Complete a todo, then click its title and fix a typo. After saving, the todo
  is unchecked again and the counter drops.
- Users silently lose their progress. The API returns `200 OK`.
- Editing the title of a todo that is not completed looks fine, which hides the
  bug in quick manual checks.

**Root cause**: the title branch also writes `completed = 0`.

```python
fields["title"] = title
fields["completed"] = 0
```

**Why it is easy to miss**
- The existing test that updates the title uses a fresh (incomplete) todo, so
  the reset has no visible effect. (That test now fails because of B10, but for
  a different reason: the title comes back empty.)
- The test that sends `title` and `completed` together passes because the later
  `completed` branch overrides the reset.

**Fix**: remove the `fields["completed"] = 0` line. Only touch fields that are
present in the request.

**Regression test**: create a todo, set `completed: true`, then `PUT` only
`{"title": "New"}`. Assert `completed` is still `true`.

### B10 — Editing a todo wipes its title

| | |
|---|---|
| **Criticality / Complexity** | Critical / Easy |
| **File** | `backend/routes.py` (`update_todo`) |

**Symptom**
- After editing a title in the UI, the todo shows an empty text. A reload shows
  the same, so the data really is lost.
- The API returns `200 OK` with `title: ""`, so there is no error message.
- Sending an empty title is still rejected with `400`, so the validation looks
  correct.

**Root cause**: the handler validates the new title but then stores an empty
string instead of it.

```python
fields["title"] = ""
```

**Why it is easy to miss**: the validation line above it is correct, and the
status code is `200`.

**Fix**: `fields["title"] = title`

**Regression test**: `PUT {"title": "Updated"}` must return `title: "Updated"`.
The existing `test_updates_title` already covers this once T1 is fixed.

### B6 — No type validation on request fields

| | |
|---|---|
| **Criticality / Complexity** | Medium / Medium |
| **File** | `backend/routes.py` (`create_todo`, `update_todo`) |

**Symptom**
- `PUT {"completed": "false"}` marks the todo as completed, because any
  non-empty string is truthy.
- `POST {"title": 123}` or `PUT {"title": 123}` raises `AttributeError`
  (`int` has no `.strip()`). Flask returns an HTML `500` page instead of the
  JSON error format the rest of the API uses.
- `PUT {"title": null}` is rejected correctly, so the checks look thorough.

**Root cause**: the handlers trust the JSON types. There is no check that
`title` is a string or that `completed` is a boolean.

**Why it is easy to miss**: the frontend always sends well-typed values, and the
tests only send strings and booleans.

**Fix**: validate types and return `400` with `{"error": ...}`:

```python
title = data.get("title")
if not isinstance(title, str) or not title.strip():
    return jsonify({"error": "title is required"}), 400
...
if "completed" in data:
    if not isinstance(data["completed"], bool):
        return jsonify({"error": "completed must be a boolean"}), 400
```

**Regression test**: parametrized test sending a non-string title and a
non-boolean `completed` and asserting `400` with an `error` key.

### B3 — Deleting a todo does not remove it from the UI

| | |
|---|---|
| **Criticality / Complexity** | Medium / Easy |
| **File** | `frontend/src/App.jsx` (`handleDelete`) |

**Symptom**
- Clicking delete sends a `204` request, but the todo stays visible and the
  counter does not update.
- Clicking delete again fails with `404` and shows "Failed to delete todo."
- Adding a todo, typing, or reloading makes the deleted todo disappear.

**Root cause**: the state updater mutates the previous array with `splice` and
returns the same reference, so React bails out of re-rendering.

```js
setTodos((prev) => {
  const index = prev.findIndex((t) => t.id === id)
  if (index !== -1) {
    prev.splice(index, 1)
  }
  return prev
})
```

**Why it is easy to miss**: `splice` is idiomatic, the backend succeeds, and a
page refresh shows the right state.

**Fix**: `setTodos((prev) => prev.filter((t) => t.id !== id))`

**Regression test**: a frontend test that deletes one item and asserts it is
removed from the DOM immediately.

### B5 — New todos appear at the bottom, not the top

| | |
|---|---|
| **Criticality / Complexity** | Low / Easy |
| **File** | `frontend/src/App.jsx` (`handleAdd`) |

**Symptom**
- A newly added todo shows up at the bottom of the list. After a page reload it
  jumps to the top, because the API returns newest first.
- The UI and the API disagree about order.

**Root cause**: the new item is appended instead of prepended.

```js
setTodos((prev) => [...prev, created])
```

**Why it is easy to miss**: with an empty list or a short list the item is
visible either way, and the app is still functionally correct.

**Fix**: `setTodos((prev) => [created, ...prev])`

**Regression test**: add two todos and assert the DOM order is newest first.

### B7 — Only 5 todos are ever loaded

| | |
|---|---|
| **Criticality / Complexity** | Critical / Easy |
| **File** | `backend/routes.py` (`list_todos`) |

**Symptom**: the list never shows more than 5 todos. After the sixth is added
and the page is reloaded, the oldest todo is missing. The data is still in the
database.

**Root cause**: a leftover `LIMIT 5` in the query.

```python
"SELECT * FROM todos ORDER BY created_at DESC, id DESC LIMIT 5"
```

**Why it is easy to miss**: the existing tests never create more than two todos.

**Fix**: remove `LIMIT 5`.

**Regression test**: create 6 todos and assert `GET /api/todos` returns 6.

### B8 — Long titles are silently cut to 20 characters

| | |
|---|---|
| **Criticality / Complexity** | High / Easy |
| **File** | `backend/routes.py` (`create_todo`) |

**Symptom**: a title longer than 20 characters is saved shortened, with no
error. The UI shows the shortened title.

**Root cause**: a slice on the title.

```python
title = (data.get("title") or "").strip()[:20]
```

**Why it is easy to miss**: all test titles are short.

**Fix**: remove `[:20]`. If a limit is wanted, reject long titles with `400`
instead of cutting them.

**Regression test**: create a todo with a 50-character title and assert the
response title is unchanged.

### B9 — The "completed" counter is always one too high

| | |
|---|---|
| **Criticality / Complexity** | Medium / Easy |
| **File** | `frontend/src/App.jsx` (footer counter) |

**Symptom**: "X / Y completed" shows one more completed todo than there really
is. With nothing ticked it reads "1 / 5 completed", and it can show more
completed than the total.

**Root cause**: an off-by-one in the count.

```jsx
{todos.filter((t) => t.completed).length + 1} / {todos.length} completed
```

**Why it is easy to miss**: there are no frontend tests, and the number still
moves in the right direction when a todo is ticked.

**Fix**: remove the `+ 1`.

**Regression test**: render two todos, one completed, and assert the text is
"1 / 2 completed".

---

## Technical bugs

### T1 — Test fixture does not isolate the database

| | |
|---|---|
| **Criticality / Complexity** | High / Medium |
| **File** | `backend/tests/test_routes.py` (`client` fixture) |

**Symptom**
- On a clean checkout several tests fail (e.g. `TypeError: 'NoneType' object is
  not subscriptable` from `todo_to_dict`).
- A second run fails more tests, e.g. `test_returns_empty_list_initially`,
  because rows from the previous run are still there.
- Running the tests writes into the developer's real `todos.db`.
- Deleting `todos.db` makes the suite "better" again, which looks like flakiness.

**Root cause**: the fixture patches a module attribute that does not exist.

```python
models.DATABASE_PATH = str(db_file)   # the real name is DB_PATH
```

`get_db()` still reads `DB_PATH`, so the temporary database is never used. No
error is raised because Python allows setting new module attributes.

**Why it is easy to miss**: the assignment looks right, there is no error, and
some tests still pass.

**Fix**: `models.DB_PATH = str(db_file)`

**Regression test**: assert in the fixture (or a test) that `models.DB_PATH`
points inside `tmp_path`, and that two consecutive test runs give identical
results.

---

## Reverting

| Bug | Revert |
|---|---|
| B1 | Restore the `"completed" in data` check in `update_todo`. |
| B2 | Change `cursor.rowcount` to `cursor.lastrowid` in `create_todo`. |
| B3 | Restore `setTodos((prev) => prev.filter((t) => t.id !== id))` in `handleDelete`. |
| B4 | Remove `fields["completed"] = 0` from the title branch of `update_todo`. |
| B5 | Restore `setTodos((prev) => [created, ...prev])` in `handleAdd`. |
| B6 | Add the `isinstance` checks shown above. |
| B7 | Remove `LIMIT 5` from the query in `list_todos`. |
| B8 | Remove the `[:20]` slice from the title in `create_todo`. |
| B9 | Remove the `+ 1` from the footer counter in `App.jsx`. |
| B10 | Change `fields["title"] = ""` back to `fields["title"] = title` in `update_todo`. |
| T1 | Set `models.DB_PATH` (not `DATABASE_PATH`) in the `client` fixture. |
