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
| 0:22 | 3 Bug | "All green, still broken" | Reproduce in the browser | Live |
| 0:27 | 4 Orchestrator | Bug or feature? | Orchestrator files the issue | Live |
| 0:32 | 5 Factory | Bug Factory section | Issue → triage → PR (+ optional Video 3) | Live |
| 0:45 | 6 Outlook | Remote agents | — | Slides |
| 0:50 | Q&A | QR code / repo link | — | |

**Trick for people following live:** the Kanban run takes 15–25 minutes. Ask
participants to *start* it during Part 1 (one prompt), then let it run in the
background while you go on. Anyone who is not done by Part 3 uses Checkpoint 1.

---

## Before the session

- [ ] **Record Video 1 and Video 2** (shot lists below). Video 3 is optional.
- [ ] **Create the checkpoint branches** in the workshop repo from the recordings:
  - `checkpoint/1-kanban` = `main` + the Kanban PR from Video 1
  - `checkpoint/2-features` = `main` + all feature PRs from Video 2, merged
  - Both must contain the sync bug (Part 3). Check it in the browser. If Bob happened
    to sync `completed → status` as well, remove that sync by hand on the checkpoint
    branches and note it in the commit message.
  - Both must still contain the rename bug (`grep -n 'data.get("completed")' todo-app/backend/routes.py`).
- [ ] Push the checkpoints to the **workshop** repo only (participants fetch them on demand,
  so their own copies never contain solutions Bob could find):
  `git push https://github.com/tschechlovdev/watch-party-building-ai-agents HEAD:checkpoint/1-kanban`
- [ ] Test the catch-up commands from WORKSHOP.md once in a fresh copy.
- [ ] Your own demo copy is set up (`./scripts/setup-bug-factory.sh`), with Checkpoint 2
  merged into its `main`, and no open bug issues or fix PRs.
- [ ] Bob IDE: a fresh conversation in *SDLC Orchestrator Agent* mode, font size large.
- [ ] Browser tabs: your demo repo (Issues, Actions, Pull requests), the app on
  `localhost:5173`, and a finished fix PR as a backup.

---

## Video 1 — Setup and the Kanban feature (target: 4 minutes)

Record in full, then cut the waiting time (speed up 8–10×, or cut and show a clock).
Put a small caption in one corner the whole time: **"Follow along: WORKSHOP.md, Part 0/1"**.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | GitHub repo page | **Use this template → Create a new repository**, leave *Include all branches* unticked | "Not clone, not fork: your own copy, so issues, Actions and Bobcoins stay yours." |
| 2 | Terminal | `gh repo clone …`, `uv run pytest` → 17 passed | "The starting point: a small todo app with tests." |
| 3 | Bob | Open folder, mode list with the five SDLC agents | "The same team as last time: orchestrator plus four specialists." |
| 4 | Bob | Orchestrator prompt: `Please run the full workflow for feature-requests/kanban-board.md` | "One prompt. Everything else is delegated." |
| 5 | Split: Bob + workflow doc | `current-role:` switching pm → architect → engineer → reviewer; sections filling in | "They never talk to each other directly. One markdown file is the shared memory." |
| 6 | Bob | Engineer running `uv run pytest`; Reviewer verdict *Approved* | "The reviewer can only read code, so it cannot fix things quietly." |
| 7 | Browser | List view, then **Board**, drag a card to *Done* | "It works." (Don't tick a checkbox in the list here, that's Part 3.) |
| 8 | Terminal / GitHub | `gh pr create`, the PR page, merge | "Every feature ends as a normal PR. A person merges." |

## Video 2 — Four features in parallel (target: 3 minutes)

Caption: **"Follow along: WORKSHOP.md, Part 2"**.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | Terminal | `gh issue create` for the features, the issue list | "Features come in as GitHub issues." |
| 2 | Terminal | `git worktree add …` ×3, then `ls ..` | "One folder per feature, one branch each, one shared history." |
| 3 | Screen grid | Three or four Bob windows, each with the orchestrator and an issue URL | "Four teams working at the same time, without getting in each other's way." |
| 4 | GitHub | Four PRs, all green | |
| 5 | GitHub / editor | A merge conflict in `App.jsx`, resolved (by hand or by Bob) | "Parallel work has a price: integration." |
| 6 | Browser | The merged app: board, priorities, due dates, search | "Everything reviewed, everything green…" (cliffhanger for Part 3) |

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

## Part 3 — live (5 min)

1. App on `main` of your demo copy. List view: tick a todo as done.
2. Switch to **Board**: the card is still in *To Do*.
3. Message: "Every PR was reviewed and green. The bug is *between* the features: Kanban
   syncs `status → completed`, but nobody syncs `completed → status`."

## Part 4 — live (5 min)

1. New conversation, *SDLC Orchestrator Agent*:
   `When I tick a todo as done in the list view, it still shows up in "To Do" on the board.`
2. Point out: it recognises a bug (Step 0 of the orchestrator skill), names the
   `file:line`, and changes no code.
3. Answer "yes" when it offers to create the issue. Switch to the browser: the issue
   has the label `bug`, and the Actions tab already shows a run.

## Part 5 — live (10 min)

Follow [`BUG-FACTORY-DEMO.md`](BUG-FACTORY-DEMO.md), sections 2–6, using the issue
from Part 4. If triage marks it as not auto-fixable, add the label `bob-fix` live:
that shows the human gate. Finish by merging the PR and repeating Part 3 in the browser.

## Part 6 — slides (5 min)

Only say what is confirmed about Bob's remote agents. The message: the factory light
already has the shape (event → agents in the cloud → PR); remote agents move the same
modes, skills and handoff files off the GitHub runner.

---

## Fallbacks

| Problem | What to do |
|---|---|
| A participant's Kanban run is slow or fails | Checkpoint 1 (WORKSHOP.md, Part 1) |
| Orchestrator starts the feature pipeline instead of reporting a bug | Stop it, start a new conversation and add "This is a bug." to the prompt |
| No triage run starts | `gh workflow run bob-bug-triage.yml -f issue-number=<n>` |
| Fix run is slow | Show the backup PR, come back to the live one in Q&A |
| The sync bug is not autofix-eligible | Add `bob-fix` live, or use the rename bug: `./scripts/setup-bug-factory.sh --demo-issue` |

## Reset after the session

```bash
gh pr close <fix-pr> --delete-branch
gh issue close <issue>
gh variable set BOB_ENABLED --body false
```
