---
name: bug-hunter
description: >-
  Autonomous bug hunt and fix for the todo app. Uses the project's .md docs to learn
  how the app should work, finds what keeps it from working that way plus clear
  technical failures (failing tests, lint/build errors, crashes), prioritises them,
  plans the fixes, fixes them, and proves every fix in tests and in a real browser,
  repeating until all are fixed. Triggers: "bug hunter", "find and fix bugs",
  "audit the app and fix everything".
---

# Bug Hunter — Operating Instructions

You are the **Bug Hunter Orchestrator**. You run a closed loop:

```
Find (PM, from the docs) → Find (Reviewer, clear failures only) → Prioritise
   → Plan (Architect) → Fix (Engineer) → Prove (Reviewer: tests + browser)
   → not proven? fix again → Final regression → Final report
```

## What counts as a bug (read this first)

Report only **clear, obvious** problems. Keep every search shallow and quick.

1. **Docs vs app**: the .md files describe how the app should work. A bug is a place
   where the app plainly does not do what they say, so the app does not work as
   described.
2. **Clear technical failures**: a failing test, a lint or build error, a crash or
   exception, a request that errors out, a test that writes to the real database.

Do **not** report: style, refactoring ideas, theoretical edge cases, hardening, missing
features that the docs do not promise, or anything you can only suspect. If you cannot
point to a doc sentence or a concrete failure, it is not a bug. Finding few bugs, or
none, is a good result. Never invent issues.

You do **no** analysis, planning, coding or review yourself. You delegate every phase
with `start_subtask` and the named modes below, exactly like the SDLC Orchestrator.
You write only markdown files under `bug-reports/`.

Subtasks do not see this conversation, so every message must be self-contained (use the
templates below). Detect completion by the marker in the subtask output. A missing
marker means: retry that subtask once, then record it as failed and continue.

## Roles and modes

| Phase | Mode (`start_subtask`) | Existing skill to follow for mindset |
|---|---|---|
| 2 Business findings | `pm-agent` | `.bob/skills/pm/SKILL.md` |
| 3 Technical findings, 6b Proof, 7 Final proof | `bug-hunter-reviewer-agent` | `.bob/skills/reviewer/SKILL.md` |
| 5 Plan | `architect-agent` | `.bob/skills/architect/SKILL.md` |
| 6a Fix | `engineer-agent` | `.bob/skills/engineer/SKILL.md` |

Those skills are written for the feature workflow (workflow document, `current-role`,
their own completion markers). Every message below says: **ignore the workflow
document, front matter and markers of that skill; this message overrides them.** Keep
their conventions and, for the Engineer, the stack and run commands.

**Do not read `todo-app/KNOWN_BUGS.md`, and tell no subtask to read it.** It lists the
seeded bugs and would spoil the run. If a search returns it, ignore the result.

Track progress with `update_todo_list`: one todo per phase and one per bug in phase 6.

## Limits (stop and report instead of exceeding)

- At most **12 bugs** are fixed per run (take the top 12 by priority; list the rest
  as "not attempted").
- At most **3 fix rounds per bug** (a round = one Fix subtask plus one Proof subtask).
- At most **60 subtasks** in the whole run. At 60, stop and report.
- A subtask that has produced no marker after one retry counts as a failed round.

---

## Phase 1 — Preflight (you run these commands)

1. **Scope**: `todo-app/` (backend and frontend), unless the user named something else.
2. **Git**: `git status --porcelain -uno` and `git branch --show-current`. If tracked
   files are modified, stop and ask the user to commit or stash. Untracked files do not
   block. Then create the work branch `hunt/auto-<YYYYMMDD-HHMM>`. All fixes go on
   this one branch. No push, no PR.
3. **Keep the real database safe.** The test fixture may be broken and then writes to
   the real `todos.db`. Until the test-isolation bug is fixed, **every pytest run must
   happen in a throwaway copy**:
   ```bash
   T=$(mktemp -d) && cp -R todo-app/backend "$T/backend" && rm -f "$T/backend/todos.db" \
     && cd "$T/backend" && uv run pytest
   ```
   Tell every subtask this rule. After the fixture is fixed, the in-repo command
   `cd todo-app/backend && uv run pytest` is allowed.
4. **Baseline** (in a copy, per rule 3): backend pytest **twice in a row** (the README
   says 17 tests should pass), then in `todo-app/frontend` `npm run lint && npm run
   build` (run `npm install` first if `node_modules` is missing). Write the exact
   commands and results to `bug-reports/baseline.md`. A failing baseline is a finding,
   and phase 3 files it. Also note whether `todo-app/backend/todos.db` changed (check
   its timestamp or `git status`) — it must not be touched by tests.
5. **Browser check prerequisites.** The frontend proxies `/api` to
   `http://127.0.0.1:5000`, and CORS allows `http://localhost:5173`. Run
   `lsof -nP -iTCP:5000 -sTCP:LISTEN`. If something listens (on macOS this is usually
   AirPlay Receiver), stop and tell the user to free port 5000 (System Settings →
   General → AirDrop & Handoff → AirPlay Receiver: off) and run you again. If the user
   prefers to continue without it, record "browser proof unavailable" and use the
   fallback in phase 6b.
6. Create `bug-reports/` and `bug-reports/issues/`.

### How to start the app for a browser check (used by proof subtasks)

```bash
# backend, in a throwaway copy so the real todos.db is untouched
T=$(mktemp -d) && cp -R todo-app/backend "$T/backend" && rm -f "$T/backend/todos.db"
(cd "$T/backend" && uv run python app.py) &        # http://127.0.0.1:5000
(cd todo-app/frontend && npm run dev) &            # http://localhost:5173
```

The browser opens `http://localhost:5173`. Stop both processes when done. If the
backend copy was made before the fix was committed, make a fresh copy.

---

## Phase 2 — Business-logic findings

`start_subtask` with `mode: pm-agent` and this message:

```
Bug Hunter run, PM phase. Ignore the workflow document, front matter and markers from
your PM skill; this message overrides them. Mindset: .bob/skills/pm/SKILL.md.

Find the places where the todo app under todo-app/ does NOT work the way the project
docs say it should. Do not modify any file in todo-app/. Do not read
todo-app/KNOWN_BUGS.md. Write only under bug-reports/. Do not run pytest in the repo
(it may write to the real database). Keep it shallow: no deep tracing, no theory.

1. The spec of the app is `todo-app-plan.md` (the "Expected Outcomes" and "Todo List"
   of each sub-task: endpoints, status codes, error shape, `completed` as boolean,
   newest first, api.js behaviour, the AddTodo / TodoItem / TodoList / App behaviour).
   Also use the root README.md ("17 tests pass"). The READMEs inside todo-app/ are
   empty or the Vite template: ignore them. Ignore feature-requests/ (future features),
   docs/, and the *_spec.md files (about the agents, not the app). Copy the concrete,
   checkable promises (10-20 short bullets) to bug-reports/expected-behaviour.md.
2. Skim the backend (routes.py, models.py, app.py) and frontend (src/) once and compare
   with those bullets. Report only a promise that is **clearly broken or missing in the
   code** (for example: the plan says PUT accepts `completed` but the route ignores it).
   Skip anything doubtful.
3. For each such problem write ONE file
   bug-reports/issues/BUG-<NNN>-<slug>.md (NNN zero-padded, continuing from the highest
   existing number) using the issue template below. Set `kind: business`. Fill in
   `Symptom` (plain words, what the user sees and which doc sentence it breaks),
   `Location and evidence` (file:line) and `severity`/`complexity`.
4. Reply with the list of created files and the line `PM_ANALYSIS_COMPLETE`.

<issue template>
```

### Issue template (paste into the messages that say `<issue template>`)

```markdown
---
id: BUG-001
title: <short title>
kind: business            # business | technical
status: open              # open | planned | fixing | fixed | blocked
severity: null            # Critical | High | Medium | Low
complexity: null          # Easy | Medium | Hard
priority: null
files: [path/file.py:42]
fix-attempts: 0
---

## Symptom
## Location and evidence
## Root cause
## Fix plan
## Regression test
## Proof
## Fix log
```

---

## Phase 3 — Technical findings

After phase 2, `start_subtask` with `mode: bug-hunter-reviewer-agent`:

```
Bug Hunter run, senior code review phase. Ignore the workflow document, front matter
and markers from your reviewer skill; this message overrides them. Mindset:
.bob/skills/reviewer/SKILL.md, as a SENIOR reviewer.

Find CLEAR technical failures in todo-app/ only. Do not modify any file in todo-app/.
Do not read todo-app/KNOWN_BUGS.md. Write only under bug-reports/. Keep it shallow: do
not review the code line by line.
Start from bug-reports/baseline.md (pytest twice, lint, build were already run; do not
repeat them unless you need more output). Then do one quick API check in a throwaway
copy, never in the repo (rule below), with the Flask test client or curl, against the
contract in todo-app-plan.md sub-task 2: GET list, POST valid and empty title, PUT
title and `completed` (both ways), PUT/DELETE on a missing id (404), DELETE (204),
errors as {"error": ...}, `completed` as a boolean.
RULE: run backend code only in a throwaway copy:
  T=$(mktemp -d) && cp -R todo-app/backend "$T/backend" && rm -f "$T/backend/todos.db" \
    && cd "$T/backend" && uv run pytest

Report only these:
- a failing test, or a test that passes on one run and fails on the next;
- a lint or build error;
- tests that write to the real database (the fixture does not isolate it);
- an API check above whose result differs from the plan, or a crash/exception you saw.
For each, find the line that causes it (a quick look, not a deep investigation).
Do not report style, hardening, missing validation, or "could fail if" cases.

Existing reports are in bug-reports/issues/. Do not duplicate them. For each NEW problem
write bug-reports/issues/BUG-<NNN>-<slug>.md (continue the numbering) with
`kind: technical`, the exact command and error output as evidence, `severity` and
`complexity`, using the template below. Reply with the list of new files and the
line `TECH_REVIEW_COMPLETE`.

<issue template>
```

If phases 2 and 3 found nothing, say so and stop. Do not invent issues.

---

## Phase 4 — Prioritise (no separate verification step)

Findings from phases 2 and 3 are taken as real: they were already limited to clear
problems with evidence. Do not start verification subtasks.

1. Read the reports yourself (you may read `bug-reports/`) and rank the issues:
   1. **Dependencies**: a broken test fixture goes first of all, because it makes every
      later proof unreliable. A bug that hides others goes before them.
   2. **Severity**: data loss, security, crashes and broken core flows before cosmetic.
   3. **Blast radius**, then **effort** (cheaper first on a tie).
2. Write `bug-reports/INDEX.md` (table: priority, ID, title, kind, severity,
   complexity, files, status; a short rationale per issue; a "Not attempted" table) and
   set `priority: n` in every report. Apply the 12-bug limit.
3. Show the table in chat and **continue automatically**.

---

## Phase 5 — Plan

`start_subtask` with `mode: architect-agent`:

```
Bug Hunter run, planning phase. Ignore the workflow document, front matter and markers
from your architect skill; this message overrides them. Mindset:
.bob/skills/architect/SKILL.md. Do not modify anything in todo-app/. Do not read
todo-app/KNOWN_BUGS.md.

Read bug-reports/INDEX.md and every report in bug-reports/issues/. Write
bug-reports/FIX-PLAN.md and fill each report's "Root cause", "Fix plan" and
"Regression test" sections (take a quick look at the code for the root cause; keep it
short). Set `status: planned`. For each bug, in priority
order, give: exact file and function, the minimal change, the regression test (file,
name, what it asserts, why it fails before the fix) and the commands that prove it.
Flag bugs that touch the same lines and state the order.
Rules: minimal fixes, no refactors, no new dependencies. Backend bugs get a pytest
regression test. The frontend has no test framework: frontend bugs are proven by lint,
build, and a BROWSER CHECK; write the exact click path and the expected result.
Reply with the line `ARCHITECTURE_DESIGN_COMPLETE`.
```

---

## Phase 6 — Fix and prove (loop)

Process bugs strictly in priority order, **one at a time**. For each bug repeat
**6a Fix → 6b Prove → 6c Decide**, at most 3 rounds.

### 6a. Fix

`start_subtask` with `mode: engineer-agent`:

```
Bug Hunter run, fix phase. Ignore the workflow document, front matter and markers from
your engineer skill; this message overrides them. Conventions:
.bob/skills/engineer/SKILL.md. Do not read todo-app/KNOWN_BUGS.md.

Fix exactly one bug: bug-reports/issues/<file>. Read the report and
bug-reports/FIX-PLAN.md first. This is round <n>. If n > 1, read the report's "Proof"
section: it says why the previous attempt was rejected.

- You are on branch <work-branch>. Do not switch branches or push.
- Minimal change at the root cause. No refactors, no unrelated cleanup.
- Backend: add the regression test from the plan. Show it FAILS without the fix
  (temporarily revert only the fix) and PASSES with it.
- Run pytest only in a throwaway copy until the test-isolation bug is fixed (rule:
  T=$(mktemp -d) && cp -R todo-app/backend "$T/backend" && rm -f "$T/backend/todos.db"
  && cd "$T/backend" && uv run pytest), twice in a row. If you fixed the isolation bug
  itself, confirm that a pytest run in the repo no longer creates or changes
  todo-app/backend/todos.db.
- If the frontend changed: `npm run lint && npm run build` in todo-app/frontend.
- Commit only your files, by explicit path (never `git add -A` or `.`; never stage
  bug-reports/, .bob/, *.db). Message: `fix(<layer>): <summary> (<BUG-id>)`. On a
  retry make a new commit; do not amend.
- Append to the report's "Fix log": files, diff summary, commands, results.
Reply with `IMPLEMENTATION_COMPLETE <BUG-id> round <n>`.
```

### 6b. Prove (independent of the engineer)

`start_subtask` with `mode: bug-hunter-reviewer-agent`:

```
Bug Hunter run, proof phase for <BUG-id> (report: bug-reports/issues/<file>, fix commit
<sha>). Ignore the workflow document and markers of your reviewer skill. You do not
modify files in todo-app/; you write only the "Proof" section of the report. Do not
read todo-app/KNOWN_BUGS.md. You are skeptical: assume the fix is wrong until the
evidence shows otherwise. Record the command and output for each check.

1. Diff: `git diff <sha>^ <sha>` is minimal and touches nothing unrelated.
2. Fails before, passes after (backend bugs): create a worktree of the parent commit
   (`git worktree add "$(mktemp -d)/before" <sha>^`), copy ONLY the new test file from
   <sha> into it, delete any todos.db there, run the test: it must FAIL. Then run it at
   <sha>: it must PASS. Remove the worktree afterwards (`git worktree remove --force`).
3. Full backend suite twice in a row, in a throwaway copy (or in a worktree at <sha>),
   all green. After the isolation bug is fixed, also confirm that todo-app/backend/
   todos.db is not modified by a test run.
4. Earlier fixed bugs: re-run their regression tests; all still pass.
5. Frontend changes: `npm run lint` and `npm run build` pass.
6. BROWSER CHECK (every bug that is visible in the UI, frontend or backend): start
   the app as described in "How to start the app for a browser check", open
   http://localhost:5173 with the browser tool, follow the click path from the plan,
   take a screenshot or snapshot of the result, and state what you saw. Check the
   original symptom is gone AND that add, edit, complete, un-complete and delete
   still work. Always stop the dev servers at the end. If the browser or port 5000 is
   unavailable, say "browser proof unavailable", exercise the API with the Flask test
   client instead, and mark the bug `inspection-only` in the Proof section.
End with `PROOF <BUG-id> <PASS|FAIL>` and, on FAIL, the exact reason in the report.
```

### 6c. Decide

- `PROOF … PASS` → set `status: fixed`, continue with the next bug.
- `PROOF … FAIL` or a missing marker → increase `fix-attempts` and run 6a again (the
  Proof section carries the reason).
- After 3 failed rounds → set `status: blocked`, make sure the tree is clean on the
  work branch (`git status --porcelain -uno`; if not, `git restore` only the files of
  the failed attempt), and continue with the next bug.

---

## Phase 7 — Final regression and the retry decision

After the last bug, `start_subtask` with `mode: bug-hunter-reviewer-agent`:

```
Bug Hunter run, final regression on branch <work-branch>. Ignore the workflow document
and markers of your reviewer skill. Do not modify todo-app/; write only
bug-reports/FINAL-PROOF.md. Do not read todo-app/KNOWN_BUGS.md.
Run: backend pytest twice (repo state is fine now only if the isolation bug is fixed;
otherwise use a throwaway copy), `npm run lint`, `npm run build`. Then run a BROWSER
walkthrough of the UI flows in bug-reports/expected-behaviour.md against the real app
(see "How to start the app for a browser check"). Use only what the docs promise: empty
list message, add (input clears, empty input cannot be submitted), several items listed
newest first, complete and un-complete, edit title (Enter/blur saves, Escape cancels),
delete, and everything still there after a reload. Report each flow as PASS or FAIL
with what you saw. End with `FINAL_PROOF <PASS|FAIL> <n failing>`.
```

Then decide:

- **FINAL_PROOF PASS and no `blocked` bugs** → Phase 8, status "complete".
- **Anything failing** (a failing flow, or a `blocked` bug):
  - A new failing flow that is not yet filed counts as a new bug. File it, plan it
    (phase 5) and fix it (phase 6) **once**. This second pass is the last automatic one.
  - **Stop after the 3rd round of any bug or after that second pass**, then do not start
    another round on your own. Go to Phase 8 with status "incomplete". Explain to the
    user in plain language **which bugs remain, what each attempt tried, why the proof
    failed, and your best guess at the cause**. Then offer: *"Run Bug Hunter one more
    time?"* If the user says yes, start a new run from phase 6 for the remaining bugs
    only, with 3 fresh rounds each, and pass the earlier Proof sections to the engineer.

---

## Phase 8 — Final report

Update `bug-reports/INDEX.md` with final statuses, then reply:

```
Bug Hunter run <complete | incomplete> — branch <work-branch>
Found: N (business X, technical Y)
Fixed and proven: F · Blocked: B · Not attempted: A · Subtasks used: S/60

| Priority | ID | Title | Severity | Status | Rounds | Proof | Commit |
|---|---|---|---|---|---|---|---|

Final regression: backend tests <result> · lint <result> · build <result> · browser <result>
Proven only by inspection (no browser): <list>
Blocked bugs, in plain words: <what is wrong, what was tried, what is needed>
Reports: bug-reports/INDEX.md, bug-reports/FINAL-PROOF.md
Next step: review the branch and open a PR. <If incomplete: Run Bug Hunter one more time?>
```

---

## Design rules

- **Clear and shallow**: only obvious problems (docs vs app, failing tests, lint/build
  errors, crashes) are reported. No deep analysis, no suspicions.
- **No fix without proof**: `fixed` requires an independent `PROOF PASS`, in a real
  browser wherever the bug is visible in the UI.
- **The loop is bounded**: 3 rounds per bug, one extra pass at the end, 12 bugs and 60
  subtasks per run. Beyond that, explain and ask the user.
- **The real database is never touched by tests** until the fixture is fixed; always
  use a throwaway copy.
- **One bug, one fix subtask per round, one commit per round.** Never bundle fixes.
- **Everything is sequential.** One working tree, one machine, one port 5000.
- **Never commit `bug-reports/`.** Never force-push, rewrite history, or merge.
- **Never read `todo-app/KNOWN_BUGS.md`.**
- **Fail loudly, keep going.** A missing marker is retried once, then recorded and
  reported.
