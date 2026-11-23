---
name: bug-hunter
description: >-
  Autonomous bug hunt and fix for the todo app. Checks the app against a fixed
  checklist of expected behaviours (taken from todo-app-plan.md), reports exactly the
  checks that fail and nothing else, fixes them in a few batches, and proves every batch
  with tests, lint and build. Triggers: "bug hunter", "find and fix bugs", "audit the
  app and fix everything".
---

# Bug Hunter — Operating Instructions

You are the **Bug Hunter Orchestrator**. You run this short loop:

```
Find (one Reviewer subtask) → Batch (you) → for each batch: Fix + plan (Engineer)
   → Prove (Reviewer) → not proven? fix again → Final check → Commit → Final report
```

A normal run is about 8 subtasks. Do not add any.

You do **no** analysis, coding or review yourself. You delegate with `start_subtask` and
the named modes below. You write only markdown files under `bug-reports/`.

## Run rules (read first)

1. **Top-level only.** You need the `start_subtask` tool. If you do not have it, you are
   inside a subtask or in the wrong mode: stop at once and reply "Bug Hunter must run as
   the top-level task in the Bug Hunter Orchestrator Agent mode. Start a new chat in
   that mode." Do nothing else. Never use `spawn_subagent`, never switch modes, never do
   a subtask's work yourself.
2. **No user interaction.** Never ask the user to switch modes, to confirm, or to
   continue. Starting this skill is the user's explicit request for the branch and the
   one commit in phase 8. The only allowed stop-and-tell is the dirty-tree check in
   phase 1. If something cannot run, mark the affected bugs `blocked`, continue, and
   finish as "incomplete" with the reason.
3. **Subtasks must close themselves.** A subtask only returns to you when it calls
   `end_subtask`. Every subtask message below ends with the **closing rule** (below);
   paste it into each message.
4. Subtasks do not see this conversation, so every message must be self-contained.
   Detect completion by the marker inside the `end_subtask` result. A missing marker
   means: retry that subtask once, then record it as failed and continue.

**Closing rule** (paste at the end of every subtask message, with the right marker):

```
Closing rule: your LAST action must be a call to the end_subtask tool whose result text
contains the marker <MARKER>. Do not ask the user anything, do not wait for input, do not
switch modes, do not use the subagent tool.
```

## The checklist (this is the whole scope)

The app is judged against **exactly these checks**. A bug is a check that FAILS. Report
every failing check, and **report nothing else**: no style, no hardening, no other ideas,
no suspicions. If all checks pass, there is nothing to fix. Keep every look shallow: read
the one function the check names, do not review the rest.

Source of the expectations: **only** `todo-app-plan.md` (the API contract and the UI
behaviour it describes). The checks are general rules; they name no specific defect.
The agent has to read the code and find out for itself whether the rule holds.

| ID | Where | The check passes only if… |
|---|---|---|
| C1 | `backend/routes.py` create | `POST /api/todos` returns the todo that was just created from the request, in full (plan: "201 with created todo"). |
| C2 | `backend/routes.py` update | `PUT /api/todos/<id>` applies every field the request provides, whatever its value (plan: "update only provided fields"). |
| C3 | `backend/routes.py` update | `PUT` changes only the fields that were provided; all other fields keep their values. |
| C4 | `backend/routes.py` update | The `PUT` response and the stored row hold exactly what the request asked for. |
| C5 | `backend/routes.py` list | `GET /api/todos` returns every todo, newest first (plan: "array of all todos (newest first)"). |
| C6 | `backend/routes.py` create | Data sent by the client is stored without being altered, apart from trimming spaces. |
| C7 | `backend/routes.py` create/update | Bad input gets `400` with `{"error": ...}`; the API never crashes or silently misreads a value (plan: "validated", "no stack traces"). |
| C8 | `frontend/src/App.jsx` | After each action (add, edit, complete, delete) confirmed by the API, the list on screen shows the result at once, without a reload. |
| C9 | `frontend/src/App.jsx` | The order on screen is the same as the order the API returns. |
| C10 | `frontend/src/` | Every number or text the UI shows about the list is correct for the data in it. |
| C11 | `backend/tests/` | The tests are isolated: they use a temporary database that the code really reads, and results are the same on every run. |
| C12 | `backend/routes.py` delete | `DELETE /api/todos/<id>` removes exactly that todo and returns `204` with no body (plan: "204 No Content"). |
| C13 | `backend/routes.py` update/delete | `PUT` and `DELETE` on an id that does not exist return `404` with `{"error": ...}` (plan: "404 if not found"). |

Frontend checks (C8–C10) are judged by reading the code.

### Criticality rubric (use it for every bug, no other scale)

- **Critical**: wrong or lost data is written, stored or returned for valid input.
- **High**: a core flow is broken (create, edit, complete, delete, list), or the API
  crashes (5xx) on input.
- **Medium**: wrong display, count or order, or bad input accepted without a crash.
- **Low**: cosmetic or documentation only.

Complexity: **Easy** = one or two lines in one place; **Medium** = several places or a
new check; **Hard** = needs a design change.

## Safe commands only

Allowed, and nothing else:

- Read-only: `ls`, `stat`, `cat`-style reads, `grep`, `git status`, `git diff`,
  `git log`, `git branch --list`.
- Tests and build: `cd todo-app/backend && uv run pytest`, and in `todo-app/frontend`:
  `npm install` (only if `node_modules` is missing), `npm run lint`, `npm run build`.
- Mkdir: `mkdir -p bug-reports/issues` (orchestrator, phase 1).
- Git, **orchestrator only**: one `git switch -c bug-fixes` (or `git switch bug-fixes`)
  at the start and one commit at the end that leaves out `bug-reports/` (see phases 1
  and 8).

**Never run**: `rm` (one exception: you delete `bug-reports/` in phase 8), `git reset`,
`git restore`, `git checkout`, `git clean`, `git stash`, `git worktree`, `git push`,
`git rebase`, `git merge`, `--force` of any kind, `sudo`, `kill`/`pkill`, `curl` or `wget`, anything that starts a server or opens a
port, or anything that deletes or overwrites files outside the edits a fix needs.
Subtasks other than the orchestrator run **no git commands that change anything** (no
branch, no commit, no add). Tell every subtask both lists.

**Edit files only with the edit/write tools, never through the shell.** Do not use
`cat > file`, `cat <<EOF`, `echo >`, `printf >`, `tee`, `sed -i`, `awk -i`, `perl -i`,
or a `python -c` / `node -e` script that writes files. Read files with the read tool
(or `cat`/`grep` for reading only). This applies to every subtask and to you.

**Do not run pytest until C11 has been checked and passes** (or its batch is fixed):
tests that are not isolated could write into the real `todos.db`. Until then, findings
come from reading the code.

**Run each command as few times as possible.** pytest, lint and build once per Fix
subtask and once per Prove subtask, not more. Do not re-run `git status` or `git diff`
without a reason.

**Do not read `todo-app/KNOWN_BUGS.md`, and tell no subtask to read it.** If a search
returns it, ignore the result.

Track progress with `update_todo_list`: one todo per phase and one per batch.

## Roles and modes

| Phase | Mode (`start_subtask`) |
|---|---|
| 2 Find, 5 Prove, 7 Final check | `bug-hunter-reviewer-agent` |
| 4 Fix (with the plan) | `engineer-agent` |

`bug-hunter-reviewer-agent` already carries the closed-pipeline rules. `engineer-agent` is
the shared SDLC mode: its role text talks about a workflow document, so the Fix message
below overrides that explicitly. The message you send is the only workflow.

## Limits (stop and report instead of exceeding)

- At most **3 fix rounds per batch** (a round = one Fix subtask plus one Prove subtask).
- At most **20 subtasks** in the whole run. At 20, stop and report.
- A subtask with no marker after one retry counts as a failed round.

---

## Phase 1 — Preflight (you run these)

1. **Guard**: check run rule 1 (you must have `start_subtask`).
2. **Scope**: `todo-app/` (backend and frontend).
3. **Git**: run `git status --short` once. If tracked files are modified, stop and tell
   the user to commit or stash (the only allowed stop). Otherwise run
   `git branch --list bug-fixes`: if it prints nothing run `git switch -c bug-fixes`,
   else run `git switch bug-fixes`. **All fixes stay on this branch, uncommitted, until
   phase 8.** No other git command until then.
4. Run `mkdir -p bug-reports/issues`. Create no other file (no `.gitkeep`).
5. If `todo-app/frontend/node_modules` is missing, run `npm install` there.

---

## Phase 2 — Find (one subtask, the whole checklist)

`start_subtask` with `mode: bug-hunter-reviewer-agent` and this message:

```
Bug Hunter run, find phase. Write only under bug-reports/. Do not edit todo-app/. Do not
read todo-app/KNOWN_BUGS.md. Keep it shallow and use targeted line-range reads (do not read
entire files top-to-bottom).
Allowed commands: read-only commands, `npm run lint` and `npm run build` in
todo-app/frontend. DO NOT RUN PYTEST (the tests might not be isolated from the real
database). Never run rm, git changes, servers or network commands. Edit files only with
your edit/write tools, never with cat >, heredocs, tee or sed -i.

This is analysis only: you must not edit any file in todo-app/.
Check the todo app against the checklist (rows C1 to C13) in .bob/skills/bug-hunter/SKILL.md.
Read only that section and the "Criticality rubric". Source of truth is todo-app-plan.md.
For each check, use targeted read_file ranges on the named functions and decide PASS or FAIL
with concrete file:line evidence.

Also run `npm run lint` and `npm run build` in todo-app/frontend; an error is a failure.

Write every result to bug-reports/checklist.md (ID, PASS/FAIL, one line of evidence with
file:line; for lint/build the command and the first error).
For every FAIL write ONE file bug-reports/issues/BUG-<NNN>-<slug>.md (NNN zero-padded,
from 001) using the issue template in .bob/skills/bug-hunter/SKILL.md: `kind: business` or
`technical`, `check: C<n>`, symptom, code location (file:line), and `criticality` and `complexity`.
Report NOTHING that is not a failing check.
Result text: the list of created files and the line `FIND_COMPLETE`.

<closing rule with marker FIND_COMPLETE>
```

### Issue template (paste into the messages that say `<issue template>`)

```markdown
---
id: BUG-001
title: <short title>
kind: business            # business | technical
check: C1
status: open              # open | planned | fixing | fixed | blocked
criticality: null         # Critical | High | Medium | Low
complexity: null          # Easy | Medium | Hard
priority: null            # set by the orchestrator, 1 = first
batch: null
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

If no check failed, say so and go straight to Phase 8 (nothing to fix, nothing to
commit). Do not invent issues.

---

## Phase 3 — Batch (you, no subtask)

No verification step: every report is a failed check and is taken as real.

1. Read the reports. Group them into **logical batches**, in this order:
   1. **Tests batch** (check C11, if it failed): first, because non-isolated tests make
      every later test run unsafe.
   2. **Backend CRUD batch**: failing checks in `todo-app/backend/routes.py` covering core
      business operations (C1 to C6: create, update fields, list ordering).
   3. **Backend Validation batch**: failing checks in `todo-app/backend/routes.py` covering
      input validation, error responses, and 400/404 handling (C7, C13). Separating
      validation prevents minor edge cases from causing full CRUD re-proof cycles.
   4. **Frontend batch**: all failing checks in `todo-app/frontend/` (C8 to C10), including
      lint and build errors.
2. Prioritise every bug yourself, from the reports only (never from KNOWN_BUGS.md):
   1. the tests batch first, if C11 failed;
   2. then by **criticality** (Critical > High > Medium > Low), as set by the rubric;
   3. then by **complexity** (Easy before Medium before Hard).
   Give each bug a `priority` number (1 = first). Fix order follows the batches; the
   priority number is for the table.
3. Write `bug-reports/INDEX.md` and show the same table in chat, listing **every bug
   found**, sorted by priority, and set `priority` and `batch: n` in every report:

   | Priority | ID | Check | Title | Criticality | Complexity | Files | Batch |
   |---|---|---|---|---|---|---|---|

   Then **continue automatically**.

---

## Phase 4 — Fix, with the plan (one subtask per batch)

For each batch in order: **4 Fix → 5 Prove → 6 Decide**, at most 3 rounds.

`start_subtask` with `mode: engineer-agent`:

```
Bug Hunter run, fix phase, batch <n>. This message is your only workflow: there is no
workflow document, no front matter, no current-role field; ignore the engineer skill and
the feature-workflow rules of your role, and any global rules about task sizing, SDLC
roles, the knowledge/ bundle or a final-report format (security rules still apply). The
app is Flask with plain sqlite3 (not SQLAlchemy) and React with Vite. Do not read
todo-app/KNOWN_BUGS.md.

You MAY edit files in todo-app/ (source and tests). Fix every bug in this batch:
<list of report files>. Read each report first. This is round <r>. If r > 1, read the
reports' "Proof" sections: they say why the last attempt was rejected.

For each bug, first fill the report's "Root cause", "Fix plan" and "Regression test"
(short, a few lines) and set `status: fixing`, then fix it.
- Minimal change at the root cause. No refactors, no unrelated cleanup, no new
  dependencies.
- Backend bugs: add one regression test per bug in todo-app/backend/tests/.
- Run `cd todo-app/backend && uv run pytest` once at the end, ONLY if C11 is PASS in
  bug-reports/checklist.md or its report is `fixed`, or this batch is the tests batch
  (then only after the fixture change). Never when C11 is `blocked`.
- Frontend bugs: no test (no test framework); run `npm run lint && npm run build` once
  at the end.
- No git commands that change anything (no branch, add, commit, checkout, restore,
  reset, stash). No rm. No servers. The orchestrator commits at the end.
- Edit files ONLY with your edit/write tools. Never with `cat >`, heredocs, `echo >`,
  `tee`, `sed -i` or a script that writes files.
- Append to each report's "Fix log" (append only, never delete earlier entries): files
  changed, what, command results. Do not set `fixed` or `blocked`; the orchestrator does.
Result text: a short summary and the line `IMPLEMENTATION_COMPLETE batch <n> round <r>`.

<closing rule with marker IMPLEMENTATION_COMPLETE>
```

If the subtask says an edit or tool was rejected, do not work around it: treat the round
as failed (phase 6).

---

## Phase 5 — Prove (one subtask per batch)

`start_subtask` with `mode: bug-hunter-reviewer-agent`:

```
Bug Hunter run, proof phase for batch <n> (reports: <list>). Do not edit todo-app/;
write only the "Proof" section of each report. Do not read todo-app/KNOWN_BUGS.md. Be
skeptical: assume the fix is wrong until the evidence shows otherwise. Allowed commands:
read-only commands, `git diff`, `uv run pytest` (only if C11 is PASS in
bug-reports/checklist.md or its report is fixed, or this is the tests batch after its
fix; never if C11 is blocked), `npm run lint`, `npm run build`. Nothing else. Run each
command once.

1. Run `git diff -- <the files of this batch>`. Inspect the diff and use targeted line-range
   reads on changed functions; do NOT re-read entire unmodified files. Changes must be
   minimal and touch only what this batch needs.
2. For each bug in the batch, verify its check row in .bob/skills/bug-hunter/SKILL.md now passes.
3. Backend: each new regression test exists and `cd todo-app/backend && uv run pytest`
   is fully green. **Exception, tests batch:** other bugs are not fixed yet, so some
   tests may still fail for unrelated reasons. For this batch only, PASS means the
   tests now use a temporary database (read the setup) and `todo-app/backend/todos.db`
   is not changed by the run (compare its modified time before and after); failing
   tests that belong to other bugs are not a reason to fail the proof.
4. Frontend change: `npm run lint` and `npm run build` pass.
Record the command and a short result for each check.
Result text: a short summary and the line `PROOF batch <n> <PASS|FAIL>`; on FAIL write
which bug and the exact reason in that report's Proof section.

<closing rule with marker PROOF>
```

---

## Phase 6 — Decide (you keep the reports up to date)

You are the only one who sets `fixed` or `blocked`, and you update the report front matter
(`status`, `fix-attempts` = number of rounds run so far) after every round.

- `PROOF … PASS` → set every report of the batch to `status: fixed`, go to the next batch.
- `PROOF … FAIL` or a missing marker → increase `fix-attempts` and repeat phase 4 for this
  batch (only the failed bugs, with the Proof sections).
- After 3 failed rounds → set the failed bugs to `status: blocked` and continue with the
  next batch. Do not undo files; the final report lists them.

---

## Phase 7 — Final check (one subtask)

After the last batch, `start_subtask` with `mode: bug-hunter-reviewer-agent`:

```
Bug Hunter run, final check. Do not edit todo-app/; write only bug-reports/FINAL-CHECK.md.
Do not read todo-app/KNOWN_BUGS.md. Allowed commands: read-only commands,
`uv run pytest`, `npm run lint`, `npm run build`. Nothing else. Run each command once.

Re-check every row C1 to C13 in .bob/skills/bug-hunter/SKILL.md against the current code using
targeted line-range reads and give PASS or FAIL with one line of evidence (file:line).
Then run `cd todo-app/backend && uv run pytest` (skip it if C11 is blocked or still
FAIL: say so instead), `npm run lint` and `npm run build`.
Report only failing checks and failing commands; add nothing else.
Result text: the failing items, if any, and the line `FINAL_CHECK <PASS|FAIL> <n failing>`.

<closing rule with marker FINAL_CHECK>
```

Then decide:

- **PASS and no `blocked` bugs** → Phase 8, status "complete".
- **A check or command fails** → file it as a new report, run phases 4 to 6 for it
  **once** as one extra batch, then run this phase again. That is the last automatic pass.
- **Still failing after that, or a `blocked` bug** → Phase 8 with status "incomplete".
  Explain in plain language which bugs remain, what each attempt tried, why the proof
  failed, and your best guess at the cause. Then offer: *"Run Bug Hunter one more
  time?"*

---

## Phase 8 — Commit and final report

1. **Read the reports now**, while they still exist, and prepare the final table below
   from their front matter (`status`, `fix-attempts`): all bugs found, with final status.
   Every report must carry its final status here; fix any stale one first.
2. Commit once, leaving out the reports (this is authorised, do not ask):
   `git add -A -- . ':!bug-reports' && git commit -m "fix: bug-hunter fixes (<n> bugs)"`
   on branch `bug-fixes`. If there is nothing to commit, skip it. Do not push. Run no
   other git command that changes anything.
3. If the run is **complete** (or nothing was found), delete the reports with
   `rm -r bug-reports`. This is the only `rm` you may run, and only on that folder. If
   the run is **incomplete**, keep `bug-reports/` (a retry needs the Proof sections) and
   say so.
4. Reply with the final report:

```
Bug Hunter run <complete | incomplete> — branch bug-fixes
Found: N (business X, technical Y) · Fixed and proven: F · Blocked: B · Subtasks: S/20

| Priority | ID | Title | Criticality | Complexity | Files | Status | Rounds |
|---|---|---|---|---|---|---|---|
(every bug found, sorted by priority)

Final check: backend tests <result> · lint <result> · build <result>
Blocked bugs, in plain words: <what is wrong, what was tried, what is needed>
Reports: <deleted | kept in bug-reports/ because the run is incomplete>
Next step: review the branch and open a PR. <If incomplete: Run Bug Hunter one more time?>
```

---

## Design rules

- **Fixed scope**: only failing checklist items are bugs. Nothing else is reported.
- **Controls**: C12 and C13 describe behaviour that is expected to hold in the seeded
  app. A FAIL there needs concrete evidence; a Find agent that fails everything is
  hallucinating. The Find prompt does not say this (so the agent cannot game it).
- **Shallow**: read the named function, do not review the rest.
- **Few subtasks**: one find, one fix and one proof per batch, one final check.
- **No fix without proof**: `fixed` requires `PROOF PASS` (tests, lint, build).
- **Bounded**: 3 rounds per batch, one extra pass at the end, 20 subtasks per run.
- **Safe commands only** (list above).
- **Git is minimal**: `git switch -c bug-fixes` at the start, one commit at the end
  (without `bug-reports/`), then `bug-reports/` is deleted when the run is complete.
- **Analysis never edits code**: only the Fix subtask changes files in `todo-app/`.
- **Autonomous**: subtasks close with `end_subtask`; nobody asks the user to switch modes;
  a blocked phase ends the run as "incomplete", never as a workaround.
- **Never read `todo-app/KNOWN_BUGS.md`.**
- **Fail loudly, keep going.** A missing marker is retried once, then recorded.
