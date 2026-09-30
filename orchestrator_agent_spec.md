# Orchestrator Agent Spec

## Goal

The Orchestrator Agent is an optional, higher-level driver that accepts a feature request and
automatically runs the full PM → (optional Architect) → Engineer → Reviewer pipeline by firing
each specialist agent as a subtask in sequence.

The Orchestrator does no PM, architecture, engineering, or review work itself — it only delegates
and verifies that each phase completed correctly before starting the next.

---

# Mode Setup

When asked to implement this spec, **create the Orchestrator Agent mode in `.bob/custom_modes.yaml`**
without asking the user whether to do so.

The mode entry follows the same pattern as the other agent modes already in `custom_modes.yaml`:

```yaml
- slug: orchestrator-agent
  name: Orchestrator Agent
  roleDefinition: >
    You are the Orchestrator Agent. You drive the full SDLC pipeline automatically by delegating
    to PM, Architect, Engineer, and Reviewer agents via subtasks. You do no implementation work
    yourself — you only sequence, verify, and report.
  customInstructions: >
    At the start of every conversation, call use_skill("orchestrator") to load your detailed
    instructions before taking any action.
  groups:
    - read
    - edit
    - command
    - mcp
```

---

# Core Responsibilities

1. Accept a feature request (inline markdown, a file path, or a GitHub issue URL).
2. Persist the feature request as a file (if it was not already one).
3. Create or resume the workflow document.
4. Drive each agent phase in sequence using subtasks.
5. Verify phase completion before starting the next phase.
6. Report the final outcome, including how to run and test the result.

---

# Workflow

```text
Feature Request
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
| **No feature specified** | Orchestrator presents a ranked recommendation from the PM and asks the user to pick |

## When no feature request is provided

The Orchestrator must **not** select a feature autonomously. Instead:

1. **If the GitHub MCP server is connected** (check by calling any lightweight GitHub tool, e.g.
   listing repos or the current user): list open GitHub issues from the repository and present
   them to the user as numbered candidates.
2. **If the `gh` CLI is authenticated** (`gh auth status` returns success): use
   `gh issue list --repo <owner>/<repo>` to fetch open issues and present them.
3. **Otherwise**: list the files in `feature-requests/` and present them as candidates.

In all three cases, show the list and ask the user to pick one — **never make the selection
automatically**.

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

- Delegate everything. The Orchestrator does no substantive work itself.
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
