# Session Runbook (presenters)

**The Agentic Development Team, Part 2: A Software Factory Light with Bob for Automated Bugfixing**

The session switches between **slides** and **live demo**. Participants follow
[`WORKSHOP-2.md`](WORKSHOP-2.md); every part there matches one part here and one slide
section. The focus is **bug fixing** (Parts 2–4). The SDLC team from Part 1 and how it
built `main` are a short recap with two videos. The Bug Factory has its own detailed
script: [`BUG-FACTORY-DEMO.md`](BUG-FACTORY-DEMO.md).

## Timeline (about 60 minutes)

| Time | Part | Slides | Demo | Format |
|---|---|---|---|---|
| 0:00 | Intro + Part 0 | Title, agenda, "Your own copy", "What is on main" | Template → own repo | Live |
| 0:04 | 1 Recap | Part 1 slides (marked *From Part 1*) | **Video 1** Kanban (4 min), **Video 2** worktrees (3 min) | Video |
| 0:16 | 2 Bug | "All green, and still broken" | Reproduce in the browser | Live |
| 0:20 | 3 Orchestrator | "Bug or feature?" | Key setup, orchestrator files the issue | Live |
| 0:28 | 4 Factory | Bug Factory section | Triage → auto-fix → PR (+ optional Video 3) | Live |
| 0:40 | 5 Outlook | Remote agents, "How much autonomy?" | — | Slides |
| 0:45 | Try it out | "Go back in time", "Try it out!" | — | Slides |
| 0:48 | Q&A | QR code / repo link | — | |

**For people following live:** a fresh copy of the template already has the bug. They
can reproduce it (Part 2) and let the orchestrator file it (Part 3) without an API key.
The Bug Factory (Part 4) needs their own Bob API key.

---

## Before the session

- [ ] Videos 1 and 2 are cut. Video 3 is optional.
- [ ] **A fresh template copy for the live demo**, for example `bug-factory-live`: only
  `main`, cloned, opened in Bob, `gh` on the right account. No key yet.
- [ ] **A backup copy** with the key set up and a finished fix PR, in case something goes
  wrong live.
- [ ] Your Bob API key in your password manager. Never show its value on screen.
- [ ] The workshop repo has `BOB_ENABLED=true` (`gh variable list -R tschechlovdev/watch-party-building-ai-agents`).
- [ ] **Checkpoints are current.** The go-back command copies *all* files of a checkpoint,
  including `docs/` and `.bob/`. If `main` changed after a checkpoint was made, rebuild
  it: take `main` and put the app code of that state on top (`todo-app/`,
  `feature-workflows/`, `feature-requests/`). Test it once in a fresh copy.
- [ ] Bob IDE: a fresh conversation in *SDLC Orchestrator Agent* mode, font size large.
- [ ] Browser tabs: your live copy (Issues, Actions, Pull requests), bob.ibm.com
  (API keys page), the app on `localhost:5173`, and the backup fix PR.

---

## Part 0 — your own copy (live, 4 min)

Show **Use this template**, *Include all branches* unticked, then the slide "What is on
main". Say: "Your copy has the agent team from Part 1 and four features it built since
then. All reviewed, all green. And a bug. That's what today is about."

## Part 1 — recap and the two videos (12 min)

The slides from Part 1 carry a *From Part 1* tag: go through them quickly. Then:
"Here is how the team built what is on `main` now."

### Video 1 — The Kanban feature (4 minutes, already recorded)

Caption: **"Build it yourself: WORKSHOP-2.md → Build it yourself, A"**. The setup check
in the video says *17 passed*: that was the state before the features. On today's `main`
it is 94. Cut that shot or say so.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | GitHub repo page | **Use this template**, *Include all branches* unticked | "Your own copy, so issues, Actions and Bobcoins stay yours." |
| 2 | Terminal | `git clone …` | |
| 3 | Bob | Mode list with the five SDLC agents | "The team from Part 1: orchestrator plus four specialists." |
| 4 | Bob | Orchestrator prompt with the Kanban issue URL | "One prompt. Everything else is delegated." |
| 5 | Split: Bob + workflow doc | `current-role:` switching pm → architect → engineer → reviewer | "One markdown file is the shared memory." |
| 6 | Bob | Engineer running `uv run pytest`; Reviewer verdict *Approved* | "The reviewer can only read code." |
| 7 | Browser | Board, drag a card to *Done* | "It works." |
| 8 | GitHub | PR, merge | "Every feature ends as a normal PR. A person merges." |

### Video 2 — Three features in parallel (3 minutes, already recorded)

Caption: **"Build it yourself: WORKSHOP-2.md → Build it yourself, B"**.

| # | Shot | Show on screen | Say |
|---|---|---|---|
| 1 | GitHub | The `feature` issues | "Features come in as GitHub issues." |
| 2 | Terminal | `git worktree add …` ×3 | "One folder per feature, one branch each, one shared history." |
| 3 | Screen grid | Three Bob Shell tabs, each with an issue URL | "Three teams at the same time." |
| 4 | GitHub | Three PRs | |
| 5 | Terminal | Merge conflict, Bob resolves it | "Parallel work has a price: integration." |
| 6 | Browser | Three filter rows stacked on top of each other | "Every PR fine on its own. Together: three toolbars." |
| 7 | Bob | The tidy-up prompt, then one toolbar | "Everything reviewed, everything green…" (cliffhanger) |
| 8 | Terminal | `git worktree remove …` ×3 | |

### Video 3 (optional) — Bob checks the fix in the browser (2 minutes)

A normal Bob conversation with the Playwright MCP server configured. Show it after
Part 4 on the slide "Optional: Bob checks the fix in the browser", or skip that slide.

| # | Shot | Show on screen |
|---|---|---|
| 1 | Bob | "Start the backend and the frontend. In the browser, tick 'Buy milk' in the list, open the board and check that the card is in Done. Take a screenshot." |
| 2 | Browser (driven by Bob) | The clicks, the board with the card in *Done* |
| 3 | Bob | Bob's answer with the screenshot |

---

## Parts 2–4 — live in your fresh copy (24 min)

### Part 2 — the bug appears (4 min)
1. Start backend and frontend. List view: tick a todo as done.
2. Switch to **Board**: the card is still in *To Do*.
3. Say: "Every PR was reviewed and green. The bug is *between* the features: Kanban
   syncs `status → completed`, but nobody syncs `completed → status`."

### Part 4 setup first — your key (3 min)
Do this before Part 3, so the issue from Part 3 starts the factory right away.
1. Browser: bob.ibm.com → sign in → **API keys** → Create, type *Inference*. Show the
   page; use your prepared key and don't show its value.
2. Terminal: `./scripts/setup-bug-factory.sh`. Paste the key when asked: "Nothing
   appears while pasting. That's on purpose. No export, no file."
3. `gh secret list` and `gh variable list`: `BOB_API_KEY` and `BOB_ENABLED true`.

### Part 3 — the orchestrator files the issue (4 min)
1. New conversation, *SDLC Orchestrator Agent*:
   `When I tick a todo as done in the list view, it still shows up in "To Do" on the board.`
2. Point out: it recognises a bug (Step 0 of the orchestrator skill), names the
   `file:line`, and changes no code.
3. Answer "yes" when it offers to create the issue.

### Part 4 — triage and auto-fix (12 min)
1. Browser, the new issue: "🤖 Bob is triaging this bug", then the triage comment with
   root cause, fix options and a regression test (about 1 min). Labels:
   `bob-triaged`, `bob-autofix-candidate`.
2. Say: "Small, clear, and I am a collaborator: so Bob goes on and fixes it. For a
   complex bug it would stop here and wait for a person to add `bob-fix`."
3. Actions tab: the fix run with Engineer, Reviewer and the test gate (about 5 min).
   Fill the wait with the slides "Same team, new job" and "Guardrails".
4. The PR `fix: … (#n)`: diff, regression test, `Fixes #n`. Merge it.
5. `git pull`, restart the backend, repeat Part 2: the card moves to *Done*.

---

## Part 5 — slides (5 min)

**Outlook:** only say what is confirmed about Bob's remote agents. The message: the
factory light already has the shape (event → agents in the cloud → PR); remote agents
move the same modes, skills and handoff files off the GitHub runner.

**"How much autonomy?":** "Triage only, fix on request, auto-fix for small bugs, or
auto-merge without anyone looking. How far you go is your decision; there is no right
or wrong. Our advice: keep a person as the final gate. Don't go to the dark side of
the factory, even if it has cookies."

## Try it out — slides (3 min)

**"Go back in time":** "Want to build the features yourself with the SDLC team? Copy an
earlier state into your `main`: the end of Part 1, or Kanban done. Four commands."
Optional: run them live in your demo copy (`checkpoint/1-kanban`), show that the
features are gone, and go back with `main`.

**"Try it out!":** "Pick a starting point and pick what you want to try: the SDLC team,
worktrees, bug fixing, the factory, or something new, like a feature factory or Bob as a
PR reviewer. You don't need a perfect plan: tell Bob what you want and let Bob guide you.
Even for hard bugs: ask Bob to make hypotheses and test each one in its own subagent,
in parallel."

---

## Fallbacks

| Problem | What to do |
|---|---|
| Orchestrator starts the feature pipeline instead of reporting a bug | Stop it, start a new conversation and add "This is a bug." to the prompt |
| No triage run starts | `gh variable list` shows `BOB_ENABLED true`? Then `gh workflow run bob-bug-triage.yml -f issue-number=<n>` |
| The sync bug is not autofix-eligible | Add `bob-fix` live: that shows the human gate |
| Fix run is slow | Show the backup PR, come back to the live one in Q&A |
| A participant's own feature run: the Engineer may not edit `todo-app/` | Switch to *Engineer Agent* by hand, then `continue` in the orchestrator (WORKSHOP-2.md, Build it yourself A) |

## Reset after the session

```bash
gh pr close <fix-pr> --delete-branch
gh issue close <issue>
gh variable set BOB_ENABLED --body false
git worktree list && git worktree prune
```
