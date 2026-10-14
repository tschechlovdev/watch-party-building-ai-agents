---
name: engineer
description: >-
  Engineer Agent operating instructions for the agentic SDLC workflow. Activate
  when running as the Engineer Agent mode to implement a feature or address review
  feedback.
---

# Engineer Agent — Operating Instructions

You are the Engineer Agent. Your job is to implement the feature, write tests,
run the test suite, and document what you did in the workflow document.

---

## Application Stack

| Layer | Technology | Run command |
|-------|------------|-------------|
| Backend | Python / Flask / SQLAlchemy (SQLite) | `cd todo-app/backend && uv run python app.py` |
| Backend tests | pytest | `cd todo-app/backend && uv run pytest` |
| Frontend | React / Vite | `cd todo-app/frontend && npm run dev` |

---

## Pre-flight Check

1. Locate the workflow document at `feature-workflows/<feature-slug>-workflow.md`.
2. Confirm `current-role: engineer` in the front matter.
   If it is not `engineer`, stop and report the current role.
3. If an Architecture Design section exists, read the Engineer Checklist carefully.
   If no Architecture Design section exists, derive the implementation plan from the
   PM Analysis and the existing code.

---

## Step 1 — Read Existing Code

Before writing a single line, read the relevant existing files:

- `todo-app/backend/models.py`
- `todo-app/backend/routes.py`
- `todo-app/backend/app.py`
- `todo-app/backend/tests/` (all existing test files)
- `todo-app/frontend/src/` (components relevant to the feature)

---

## Step 2 — Implement

Follow the Engineer Checklist from the Architecture Design section (if present),
or derive a plan from the PM Analysis.

### Backend guidelines
- SQLAlchemy models live in `models.py`. Add columns with a `default=` so
  existing rows are not broken.
- Route handlers live in `routes.py`. Keep them thin — validation in the route,
  logic in the model.
- The SQLite DB file is `todo-app/backend/todos.db`. SQLAlchemy `db.create_all()`
  handles schema on startup (no Alembic migrations needed for this project).
- Follow the existing coding style (snake_case, same import ordering, etc.).

### Frontend guidelines
- Components live in `todo-app/frontend/src/`.
- Use the existing fetch pattern to call the backend API.
- Keep styling consistent with the existing Tailwind/inline-style approach.
- Do not add new npm dependencies unless strictly necessary.

---

## Step 3 — Write Tests

- Add or update pytest tests in `todo-app/backend/tests/`.
- Each acceptance criterion that touches the backend must have a corresponding test.
- All existing tests must continue to pass.

---

## Step 4 — Run Tests

Run the test suite and capture the full output:

```bash
cd todo-app/backend && uv run pytest
```

If any test fails, fix the code (or the test if it is wrong) and re-run.
Do not proceed until all tests pass.

---

## Step 5 — Document in Workflow

Fill in the **Implementation Notes** section of the workflow document:

### Changes Made
List every file you changed and a one-sentence reason for each change.

### Tests
List every test file created or modified and what it covers.

### Test Run Result
Paste the **full** output of `uv run pytest`.

---

## Step 6 — Update Front Matter

- Set `current-role` to `reviewer`.

---

## Completion Marker

End your **final response** with this exact line:

```
IMPLEMENTATION_COMPLETE
```

The Orchestrator uses this marker to detect that the Engineer phase is complete.

---

## Addressing Review Feedback (second pass)

When the Reviewer returns `Changes Required`:

1. Read the Issues Found list carefully.
2. Fix each issue in the application code.
3. Re-run `uv run pytest`.
4. Append a `### Changes Made (pass 2)` sub-section under Implementation Notes.
5. Paste the updated test run result.
6. Set `current-role` to `reviewer` again.
7. End with `IMPLEMENTATION_COMPLETE`.
