# Session Runbook (presenters)

The session switches between **slides** and **hands-on**. Participants follow
[`WORKSHOP.md`](WORKSHOP.md); every part there matches one part here and one slide
section. The Bug Factory part has its own detailed script:
[`BUG-FACTORY-DEMO.md`](BUG-FACTORY-DEMO.md).

## Timeline (about 60 minutes)

| Time | Part | Slides | Hands-on | Format |
|---|---|---|---|---|
| 0:00 | Intro + Part 0 | Title, agenda, "Your own copy" | Template → own repo → open in Bob | Live (2 min) |
| 0:05 | 1 Kanban | Recap: SDLC team, orchestrator flow | **Video 1** (4 min) | Video |
| 0:15 | 2 Parallel | Worktrees | **Video 2** (3 min) | Video |
| 0:22 | 3 Bug | "All green, still broken" | Checkpoint 2 in a fresh copy, reproduce | Live |
| 0:27 | 4 Orchestrator | Bug or feature? | Key setup, orchestrator files the issue | Live |
| 0:32 | 5 Factory | Bug Factory section | Triage → auto-fix → PR (+ optional Video 3) | Live |
| 0:42 | 6 Outlook | Remote agents, "How much autonomy?" | — | Slides |
| 0:47 | Try it out | "Try it out!" | Checkpoints, ideas, let Bob guide you | Slides |
| 0:50 | Q&A | QR code / repo link | — | |

**Trick for people following live:** the Kanban run takes 15–25 minutes. Ask
participants to *start* it during Part 1 (one prompt), then let it run in the
background while you go on. Anyone who is not done by Part 3 uses Checkpoint 1.

---

## Before the session

- [ ] **Record Video 1 and Video 2** (shot lists below). Video 3 is optional.
- [ ] **Refresh the checkpoints after doc changes.** The catch-up copies *all* files of a
  checkpoint, including `docs/` and `.bob/`. If `main` changed after a checkpoint was
  made, rebuild it: take `main` and put the feature code from the checkpoint on top.
- [ ] **Create the checkpoint branches** in the workshop repo from the recordings:
  - `checkpoint/1-kanban` = `main` + the Kanban PR from Video 1
  - `checkpoint/2-features` = `main` + all feature PRs from Video 2, merged
  - Both must contain the sync bug (Part 3). Check it in the browser. If Bob happened
    to sync `completed → status` as well, remove that sync by hand on the checkpoint
    branches and note it in the commit message.
  - `checkpoint/2-features` includes the UI tidy-up (WORKSHOP.md Part 2, step 6).
- [ ] In your recording copy, every feature issue that was built is closed (PRs with
  `Closes #<n>`, or `gh issue close <n>`).
- [ ] Push the checkpoints to the **workshop** repo only (participants fetch them on demand,
  so their own copies never contain solutions Bob could find):
  `git push https://github.com/tschechlovdev/watch-party-building-ai-agents HEAD:checkpoint/1-kanban`
- [ ] Test the catch-up commands from WORKSHOP.md once in a fresh copy.
- [ ] A **fresh** template copy for the live part (Parts 3–5 above): only `main`, no
  checkpoint, no key yet. Plus a backup copy that already has Checkpoint 2, the key and a
  finished fix PR, in case something goes wrong live.
- [ ] Bob IDE: a fresh conversation in *SDLC Orchestrator Agent* mode, font size large.
- [ ] Browser tabs: your demo repo (Issues, Actions, Pull requests), the app on
  `localhost:5173`, and a finished fix PR as a backup.

---

## Video 1 — Setup and the Kanban feature (target: 4 minutes)

Record in full, then cut the waiting time (speed up 8–10×, or cut and show a clock).
Put a small caption in one corner the whole time: **"Follow along: WORKSHOP.md, Part 0/1"**.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | GitHub repo page | **Use this template → Create a new repository**, leave *Include all branches* unticked | "Not clone, not fork: your own copy, so issues, Actions and Bobcoins stay yours. You don't have to build everything: later you can start from a checkpoint, for example with the Kanban board already done." |
| 2 | Terminal | `git clone https://github.com/<you>/my-agent-team.git` | "Plain git is enough here." |
| 2b | Terminal | The setup check from WORKSHOP.md Part 0 (versions + `uv run pytest -q` → 17 passed) | "One minute to check. If something is missing, ask Bob about that one thing." |
| 3 | Bob | Open folder, mode list with the five SDLC agents | "The same team as last time: orchestrator plus four specialists." |
| 3b | Terminal / GitHub (optional) | `./scripts/create-feature-issues.sh`, then the Issues tab with six `feature` issues | "Features come in as GitHub issues, like in a real team." |
| 4 | Bob | Orchestrator prompt with the Kanban issue URL (or `feature-requests/kanban-board.md`) | "One prompt. Everything else is delegated." |
| 5 | Split: Bob + workflow doc | `current-role:` switching pm → architect → engineer → reviewer; sections filling in | "They never talk to each other directly. One markdown file is the shared memory." |
| 6 | Bob | Engineer running `uv run pytest`; Reviewer verdict *Approved* | "The reviewer can only read code, so it cannot fix things quietly." |
| 7 | Browser | List view, then **Board**, drag a card to *Done* | "It works." (Don't tick a checkbox in the list here, that's Part 3.) |
| 8 | Terminal / GitHub | `gh pr create`, the PR page, merge | "Every feature ends as a normal PR. A person merges." |

## Video 2 — Three features in parallel (target: 3 minutes)

Caption: **"Follow along: WORKSHOP.md, Part 2"**.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | GitHub | The `feature` issues created in Video 1 | "Starting here? Copy in checkpoint 1 first, it has the Kanban board. Features come in as GitHub issues." |
| 2 | Terminal | `git worktree add …` ×3, then `git worktree list` | "One folder per feature, one branch each, one shared history." |
| 3 | Screen grid | Three Bob Shell tabs (or IDE windows), each `bob chat --mode orchestrator-agent` with an issue URL | "Three teams working at the same time, without getting in each other's way." |
| 4 | GitHub | Three PRs with `Closes #<n>` | |
| 5 | Terminal | Merge conflict after the first merge, `git merge origin/main`, Bob resolves it | "Parallel work has a price: integration." |
| 6 | Browser | The merged app: three filter rows stacked on top of each other | "Every PR fine on its own. Together: three toolbars." |
| 7 | Bob | The tidy-up prompt (WORKSHOP.md Part 2, step 6), then the app with one toolbar and the board | "Everything reviewed, everything green…" (cliffhanger for Part 3) |
| 8 | Terminal | `git worktree remove …` ×3 | "Clean up the folders." |

## Video 3 (optional) — Bob checks the fix in the browser (target: 2 minutes)

No QA agent and no extra mode: a normal Bob conversation with the Playwright MCP
server configured. Show it on the slide "Optional: Bob checks the fix in the browser"
after Part 5, or skip that slide.

| # | Shot | Show on screen |
|---|---|---|
| 1 | Bob | Prompt: "Start the backend and the frontend. In the browser, tick 'Buy milk' in the list, open the board and check that the card is in Done. Take a screenshot." |
| 2 | Browser (driven by Bob) | The clicks happening, the board with the card in *Done* |
| 3 | Bob | Bob's answer with the screenshot |

---

## Parts 3–5 — live, from a checkpoint (20 min)

You do this live in a **fresh copy** of the template, so participants see every step
they need themselves: jump to a checkpoint, store the key, and let the factory work.

**Prepare (before the session):** a fresh template copy `bug-factory-live` (only `main`),
cloned, opened in Bob, `gh` on the right account. Nothing else: no checkpoint, no key.
Have your Bob API key ready in your password manager.

### Step 1 — Jump to Checkpoint 2 (2 min)
```bash
git fetch https://github.com/tschechlovdev/watch-party-building-ai-agents checkpoint/2-features
git restore --source=FETCH_HEAD --staged --worktree :/
git commit -m "Start from checkpoint 2" && git push
```
Say: "Anyone can start here. Four commands, and you have everything from the videos,
including a bug we haven't found yet."

### Step 2 — Part 3: the bug appears (3 min)
1. Start backend and frontend. List view: tick a todo as done.
2. Switch to **Board**: the card is still in *To Do*.
3. Say: "Every PR was reviewed and green. The bug is *between* the features: Kanban
   syncs `status → completed`, but nobody syncs `completed → status`."

### Step 3 — Part 5 setup: your key (3 min)
Do this before Part 4, so the issue from Part 4 starts the factory right away.
1. Browser: bob.ibm.com → sign in → **API keys** → Create, type *Inference* (show the
   page; use your prepared key, don't show its value).
2. Terminal: `./scripts/setup-bug-factory.sh`. Paste the key when asked: "Nothing
   appears while pasting. That's on purpose."
3. `gh secret list` and `gh variable list`: `BOB_API_KEY` and `BOB_ENABLED true`.

### Step 4 — Part 4: the orchestrator files the issue (4 min)
1. New conversation, *SDLC Orchestrator Agent*:
   `When I tick a todo as done in the list view, it still shows up in "To Do" on the board.`
2. Point out: it recognises a bug (Step 0 of the orchestrator skill), names the
   `file:line`, and changes no code.
3. Answer "yes" when it offers to create the issue.

### Step 5 — Part 5: triage and auto-fix (8 min)
1. Browser, the new issue: "🤖 Bob is triaging this bug", then the triage comment with
   root cause, fix options and a regression test (about 1 min). Labels:
   `bob-triaged`, `bob-autofix-candidate`.
2. Say: "Small, clear, and I am a collaborator: so Bob goes on and fixes it. For a
   complex bug it would stop here and wait for a person to add `bob-fix`."
3. Actions tab: the fix run with Engineer, Reviewer and the test gate (about 5 min).
   Fill the wait with the slides "Same team, new job" and "Guardrails".
4. The PR `fix: … (#n)`: diff, regression test, `Fixes #n`. Merge it.
5. `git pull`, restart the backend, repeat Step 2: the card moves to *Done*.

Details and backup: [`BUG-FACTORY-DEMO.md`](BUG-FACTORY-DEMO.md).

## Part 6 — slides (5 min)

**Outlook:** only say what is confirmed about Bob's remote agents. The message: the
factory light already has the shape (event → agents in the cloud → PR); remote agents
move the same modes, skills and handoff files off the GitHub runner.

**"How much autonomy?":** "Triage only, fix on request, auto-fix for small bugs, or
auto-merge without anyone looking. How far you go is your decision; there is no right
or wrong. Our advice: keep a person as the final gate. Don't go to the dark side of
the factory, even if it has cookies."

## Try it out — slides (3 min)

On the slide "Try it out!": "15 minutes are not enough to do all of this yourself.
Pick a checkpoint and pick what you want to try: the SDLC team, worktrees, bug fixing,
the factory, or something new, like a feature factory or Bob as a PR reviewer. You
don't need a perfect plan: tell Bob what you want and let Bob guide you. Even for hard
bugs: ask Bob to make hypotheses and test each one in its own subagent, in parallel."

---

## Fallbacks

| Problem | What to do |
|---|---|
| A participant's Kanban run is slow or fails | Checkpoint 1 (WORKSHOP.md, Part 1) |
| The Engineer subtask may not edit `todo-app/` | Switch to *Engineer Agent* by hand, then `continue` in the orchestrator (WORKSHOP.md, Part 1) |
| Orchestrator starts the feature pipeline instead of reporting a bug | Stop it, start a new conversation and add "This is a bug." to the prompt |
| No triage run starts | `gh workflow run bob-bug-triage.yml -f issue-number=<n>` |
| Fix run is slow | Show the backup PR, come back to the live one in Q&A |
| The sync bug is not autofix-eligible | Add `bob-fix` live: that shows the human gate |

## Reset after the session

```bash
gh pr close <fix-pr> --delete-branch
gh issue close <issue>
gh variable set BOB_ENABLED --body false
git worktree list && git worktree prune   # remove leftover worktrees from Video 2
```
