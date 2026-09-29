# Workshop Instructions — Building an Agentic SDLC Team with Bob

This guide walks you through setting up and running the project from scratch as a workshop participant.

> **Completed solution?** Switch to the `sdlc-agents-solution` branch to see the finished implementation.

---

## Prerequisites

| Tool | Required for |
|---|---|
| [IBM Bob](https://bob.ibm.com) | Running the agent workflow |
| Python 3.11+ with [`uv`](https://github.com/astral-sh/uv) | Backend tests (`uv run pytest`) |
| Node.js 18+ | Frontend dev server |
| Git | Cloning and branching |
| GitHub account + PAT | Optional — only needed for real Issues and PRs |

---

## Step 1 — Clone and open the project

```bash
git clone https://github.com/tschechlovdev/watch-party-building-ai-agents.git
cd watch-party-building-ai-agents
```

Open the `watch-party-building-ai-agents/` folder as your Bob workspace.

---

## Step 2 — Verify the Todo application

```bash
cd todo-app/backend
uv run pytest
# Expected: all tests pass
```

---

## Step 3 — Understand the specs

Read the two spec files before you start building. They define what you need to implement and in what order:

| File | What it covers |
|---|---|
| [`sdlc_agents_spec.md`](../sdlc_agents_spec.md) | **Phase 1** — the four core agent roles, the handoff document, and PM branch creation |
| [`orchestrator_agent_spec.md`](../orchestrator_agent_spec.md) | **Phase 2** — the optional Orchestrator that drives all agents automatically |

**Build Phase 1 first.** The core agents work standalone and are the foundation everything else builds on.

---

## Step 4 — Build Phase 1: Core Agents

You will create five Bob artefacts for each agent role: a **mode** entry in `.bob/custom_modes.yaml` and a **skill** file at `.bob/skills/<name>/SKILL.md`.

The four roles are:

| Role | What it does |
|---|---|
| **PM Agent** | Reads the feature request, creates a git feature branch, writes user stories and acceptance criteria |
| **Architect Agent** | Reads the PM Analysis, designs DB schema, API changes, and frontend changes |
| **Engineer Agent** | Implements the Architecture Design, writes tests, runs them |
| **Reviewer Agent** | Reviews the implementation against the acceptance criteria, writes a verdict |

### Suggested order

1. Create the **shared workflow template** (`templates/feature-workflow.md`) — this is the handoff document all agents read and write.
2. Implement the **PM Agent** mode + skill.
3. Test it end-to-end on a feature request from `feature-requests/`.
4. Add **Architect**, **Engineer**, and **Reviewer** one at a time, testing each before moving on.

### Key design constraints

- Agents communicate **only** through the workflow document — no direct calls between them.
- Each agent reads the section written by the previous one and appends its own.
- The `current-role` field in the document's front matter controls who acts next.
- The PM Agent must create a local git feature branch (`git checkout -b feature/<slug>`) **before writing anything**.
- The Reviewer must not be able to edit source files (enforce via `fileRegex` write restriction in the mode config).

---

## Step 5 — Run the workflow

Once all four agents are implemented, pick a feature request and run the pipeline manually:

1. **PM Agent mode** → `Please analyze the feature request at feature-requests/add-priorities.md and create the workflow document.`
2. **Architect Agent mode** → `Please design the implementation for feature-workflows/add-priorities-workflow.md`
3. **Engineer Agent mode** → `Please implement feature-workflows/add-priorities-workflow.md`
4. **Reviewer Agent mode** → `Please review feature-workflows/add-priorities-workflow.md`

If the Reviewer returns **Changes Required**, switch back to Engineer Agent and run:
```
Please address the review feedback in feature-workflows/add-priorities-workflow.md
```
Then run the Reviewer again.

---

## Step 6 — Build Phase 2: Orchestrator Agent (optional)

Once Phase 1 is working, add the **Orchestrator Agent** following [`orchestrator_agent_spec.md`](../orchestrator_agent_spec.md).

The Orchestrator is a new Bob mode + skill that accepts a feature request and drives the full PM → Architect → Engineer → Reviewer pipeline automatically by firing each agent as a `start_subtask` call.

Switch to **Orchestrator Agent** mode and send:
```
Please run the full workflow for feature-requests/add-priorities.md
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `use_skill` returns "skill not found" | Bob has not scanned the workspace skills yet — **close this conversation, open a new one**, and try again |
| `uv run pytest` fails with "command not found" | `brew install uv` or `pip install uv` |
| Tests fail with "no such column" | Delete `todo-app/backend/todos.db` — it will be recreated with the correct schema |
| Bob ignores skill instructions | Confirm the mode's `customInstructions` references `use_skill` with the correct skill name, and that the skill file exists at `.bob/skills/<name>/SKILL.md` |

---

## Feature request catalogue

| File | Feature | Complexity | Good starting point? |
|---|---|---|---|
| `add-priorities.md` | **Priorities** | ⭐ Low | ✅ Recommended first run |
| `add-due-dates.md` | **Due Dates** | ⭐⭐ Low–Medium | Date handling + overdue highlighting |
| `add-search.md` | **Search & Filter** | ⭐⭐ Medium | No schema change — pure frontend |
| `add-tags.md` | **Tags / Labels** | ⭐⭐ Medium | Many-to-many DB pattern |
| `kanban-board.md` | **Kanban Board** | ⭐⭐⭐ Medium–High | Already in solution branch |
| `analytics-dashboard.md` | **Analytics** | ⭐⭐⭐ High | Aggregation API + charting |
