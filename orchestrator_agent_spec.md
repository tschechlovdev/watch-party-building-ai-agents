# Orchestrator Agent Spec

## Goal

The Orchestrator Agent is an optional, higher-level driver that automatically runs the full PM → (optional Architect) → Engineer → Reviewer pipeline by firing
each specialist agent as a subtask in sequence.

The Orchestrator does no PM, architecture, engineering, or review work itself — it only handles feature intake (selection, branch, workflow document), delegates the specialist phases, and verifies that each phase completed correctly before starting the next.

It may take as input a feature request but does not have to. If no feature request is provided, the Orchestrator itself analyses the available candidate features (by complexity and benefit) and recommends one. The user confirms the recommendation or picks another feature. Once a feature is confirmed, the Orchestrator creates the git feature branch and the workflow document, then hands over to the PM.

---

# Mode Setup

When asked to implement this spec, **create the Orchestrator Agent mode in `.bob/custom_modes.yaml`**
without asking the user whether to do so.

---

# Core Responsibilities

1. Might accept a feature request (inline markdown, a file path, or a GitHub issue URL). If none is given, analyse candidate features (complexity and benefit), recommend one, and let the user confirm or pick another.
2. Persist the feature request as a file (if it was not already one).
3. Create (or check out, when resuming) the git feature branch `feature/<feature-slug>`.
4. Create or resume the workflow document from `templates/feature-workflow.md` (with `branch` set and `current-role: pm`).
5. Drive each agent phase in sequence using subtasks.
6. Verify phase completion before starting the next phase.
7. Report the final outcome, including how to run and test the result.

---

# Workflow

```text
Feature Request (optional - Orchestrator recommends a feature otherwise; user confirms or picks another)
    ↓
Orchestrator: create feature branch + workflow document
    ↓
PM Agent subtask
    ↓
Architect Agent subtask (optional — skipped when PM sets needs-architect: false)
    ↓
Engineer Agent subtask (pass 1)
    ↓
Reviewer Agent subtask
    ↓
[Approved]  →  Done
[Changes Required]  →  Engineer Agent subtask (pass 2)  →  Reviewer Agent subtask (pass 2)
    ↓
How-to-Test Report + Final Report
```

---

# Input Handling

The Orchestrator accepts the feature request in one of four ways:

| Mode | Description |
|------|-------------|
| **Inline markdown** | User pastes or describes the feature in their message |
| **File path** | User points to an existing `feature-requests/<name>.md` file |
| **GitHub issue URL** | e.g. `https://github.com/org/repo/issues/42` — fetched via GitHub MCP or `gh` CLI (via `gh issue view` ) |
| **No feature specified** | The Orchestrator itself analyses the candidate features by complexity and benefit and recommends one. The user has to confirm this or can select another feature.|

## When no feature request is provided

The Orchestrator must **not** select a feature autonomously. Instead it discovers, analyses and
recommends:

1. **Discover candidates**, in priority order:
   - **GitHub MCP server connected** (check by calling any lightweight GitHub tool, e.g. listing
     repos or the current user): list open, unassigned GitHub issues from the repository.
   - **`gh` CLI authenticated** (`gh auth status` returns success): use
     `gh issue list --repo <owner>/<repo>` to fetch open issues.
   - **Otherwise**: list the `.md` files in `feature-requests/`.
2. **Analyse each candidate** on two dimensions:
   - **Complexity** (Low / Medium / High) — number of layers touched (DB, API, frontend), schema
     migrations required, external dependencies, test surface area.
   - **Benefit** (Low / Medium / High) — explicit priority/label metadata, keywords such as
     "urgent", "user-requested", "high-value", or how fundamental the capability is to the
     application.
3. **Present a ranked recommendation table** (`#`, Feature, Complexity, Benefit,
   Recommendation) with a one-sentence rationale for the top recommendation.
4. **Ask the user to confirm**:
   > "I recommend starting with **[feature name]**. Shall I proceed with this one, or would you
   > like to pick a different feature from the list?"

**Never make the selection automatically.** Do not create a branch, a workflow document, or any
other file until the user has confirmed the recommendation or chosen another feature.

## Feature Intake (after the feature is confirmed)

Once a feature is determined (provided by the user, or confirmed/picked after the
recommendation), the Orchestrator — not the PM Agent — performs these steps, in order, before
starting the PM subtask:

1. **Persist the feature request** as `feature-requests/<feature-slug>.md` if it is not already a
   file (inline text or GitHub issue content).
2. **Create the git feature branch**:
   ```text
   git checkout -b feature/<feature-slug>
   ```
   If the branch already exists (resuming), run `git checkout feature/<feature-slug>` instead. If
   git is unavailable or the command fails, log a warning and continue.
3. **Create the workflow document** `feature-workflows/<feature-slug>-workflow.md` from
   `templates/feature-workflow.md`: fill in `feature`, `slug`, `feature-request-file`, set
   `branch` to the branch name and `current-role: pm`. If it already exists, resume it instead
   of overwriting.
4. Start the PM Agent subtask.

## Fetching a GitHub issue

If a GitHub issue URL is provided, prefer the GitHub MCP server if available. Fall back to the
`gh` CLI:

```
gh issue view <number> --repo <owner>/<repo> --json title,body,labels,assignees,milestone
```

If neither is available, ask the user to paste the issue text directly — do not attempt a web
fetch.

---

# Architect Phase — Optional

The Architect phase is optional and controlled by the `needs-architect` flag the PM Agent writes
to the workflow document front matter.

- `needs-architect: false` → skip the Architect phase entirely and proceed directly to the Engineer.
- `needs-architect: true` (or missing) → run the Architect subtask before the Engineer.

The Orchestrator must never run the Architect phase unless the PM explicitly set `needs-architect: true`.

---

# Phase Completion Signals

Each subtask agent signals completion with a structured marker block in its final output.
The Orchestrator treats the presence of the marker as the only signal to proceed.

| Phase | Marker | Expected next `current-role` |
|-------|--------|------------------------------|
| PM | `PM_ANALYSIS_COMPLETE` | `architect` |
| Architect | `ARCHITECTURE_DESIGN_COMPLETE` | `engineer` |
| Engineer | `IMPLEMENTATION_COMPLETE` | `reviewer` |
| Reviewer | `REVIEW_COMPLETE` | `done` (approved) or `engineer` (changes required) |

If a subtask ends without the expected marker, the Orchestrator must stop and report the failure
to the user — it must never assume completion.

---

# Reviewer Verdict Handling

After the Reviewer subtask completes, read the `## Review Feedback > Verdict` field:

- **Approved** → pipeline is done; go to the Final Report.
- **Changes Required** → run the Engineer subtask a second time to address the feedback,
  then run the Reviewer subtask a second time.

The Orchestrator must not loop more than twice (Engineer pass 1 → Reviewer → Engineer pass 2 →
Reviewer). If the second review also results in Changes Required, stop and escalate to the user.

---

# Design Principles

- Delegate the specialist work. The Orchestrator does no PM, architecture, engineering or review work itself; its own work is limited to feature intake (recommendation, branch, workflow document).
- Fail loudly. If a subtask does not complete correctly, stop immediately and report the exact
  missing section — never silently skip a validation.
- Architect is optional. Never add it to the pipeline unless explicitly requested by the PM.
- Bounded retries. Engineer + Reviewer may cycle at most twice; further retries require human
  judgement.
- Resume-friendly. If a workflow document already exists and `current-role` is not `done`,
  resume from that role rather than restarting from scratch.
- Never auto-select. When presenting feature candidates, always ask the user to choose — the
  Orchestrator proposes, the human decides.

---

# Final Report

Once the workflow reaches `current-role: done`, the Orchestrator produces a final report that
includes both the pipeline summary **and actionable instructions for trying out the feature**:

```text
✅  Feature: <feature name>
📄  Workflow document: feature-workflows/<slug>-workflow.md
🔍  Final Status: <Outcome line from workflow document>
🧪  Tests: passed (confirmed by Engineer subtask)
➡️  Next step: create a pull request

---

## 🚀 How to try the feature

### Start the backend
cd todo-app/backend
uv run python app.py
# Backend runs at http://localhost:5000

### Start the frontend
cd todo-app/frontend
npm install      # first time only
npm run dev
# Frontend runs at http://localhost:5173

### What to click / test in the UI
<concrete steps specific to the implemented feature, e.g.:>
1. Open http://localhost:5173 in your browser.
2. Create a new todo — you should see a Priority dropdown with Low / Medium / High.
3. Create one High-priority item and one Low-priority item.
4. Verify the High item appears above the Low item in the list.
5. Edit an existing todo and change its priority — the badge should update immediately.
```

The "What to click / test in the UI" steps must be specific to the feature that was just
implemented. The Orchestrator derives them from the acceptance criteria in the workflow document —
do not copy the criteria verbatim; translate them into concrete UI actions a non-technical user
can follow.

---

# Relationship to the Core SDLC Agents

The Orchestrator is an *optional coordination layer* on top of the core agents defined in
[`sdlc_agents_spec.md`](sdlc_agents_spec.md). The core agents (PM, Architect, Engineer, Reviewer)
can be run manually without the Orchestrator; the Orchestrator simply automates the handoffs.

This separation means:
- The core agents can be demonstrated and validated independently.
- The Orchestrator can be introduced as a second enhancement without changing any agent behaviour.
- Teams that prefer manual control can use the core agents directly.
