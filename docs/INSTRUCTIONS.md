# Workshop Instructions — Building an Agentic SDLC Team with Bob

This lab guide walks you through setting up and running the project from scratch as a workshop participant.

> 💡 **Looking for the completed solution?** Switch to the `sdlc-agents-solution` branch (`git checkout origin/sdlc-agents-solution`) to see the finished implementation and ready-to-use `.bob/` configuration.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1 — Clone and Open the Project](#step-1--clone-and-open-the-project)
3. [Step 2 — Verify the Todo Application](#step-2--verify-the-todo-application)
4. [Step 3 — Understand the Architecture & Specs](#step-3--understand-the-architecture--specs)
5. [Step 4 — Build Phase 1: Core Specialist Agents](#step-4--build-phase-1-core-specialist-agents)
6. [Step 5 — Run the Feature Pipeline](#step-5--run-the-feature-pipeline)
7. [Step 6 — Build Phase 2: SDLC Orchestrator Agent](#step-6--build-phase-2-sdlc-orchestrator-agent)
8. [Feature Catalogue](#feature-catalogue)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Purpose |
|---|---|
| [IBM Bob](https://bob.ibm.com) | Running the agent workflow |
| Python 3.11+ with [`uv`](https://github.com/astral-sh/uv) | Backend tests (`uv run pytest`) |
| Node.js 18+ | Frontend dev server |
| Git | Cloning and branching |
| GitHub account + PAT | Optional — only needed for real Issues and PRs |

---

## Step 1 — Clone and Open the Project

### 1. In your Terminal:
```bash
git clone https://github.com/tschechlovdev/watch-party-building-ai-agents.git
cd watch-party-building-ai-agents
```

### 2. In IBM Bob:
* Open the **IBM Bob** desktop app (or Bob in VS Code).
* Go to the top menu: **File → Open Folder...** (or press `Cmd+O` on macOS / `Ctrl+O` on Windows/Linux).
* Select the `watch-party-building-ai-agents` directory.

---

## Step 2 — Verify the Todo Application

Run the existing backend test suite to make sure your environment is properly set up:

```bash
cd todo-app/backend
uv run pytest
# Expected: 17 passed
cd ../..
```

---

## Step 3 — Understand the Architecture & Specs

Before creating any files, review the specifications and markdown templates in this repository:

| File | What it covers |
|---|---|
| [`sdlc_agents_spec.md`](../sdlc_agents_spec.md) | **Phase 1** — The 4 core agent roles, the shared markdown handoff document, and branch management |
| [`orchestrator_agent_spec.md`](../orchestrator_agent_spec.md) | **Phase 2** — The optional Orchestrator that automates all handoffs via subtasks |
| [`templates/feature-workflow.md`](../templates/feature-workflow.md) | The blank handoff template that serves as the shared memory for each feature |

---

## Step 4 — Build Phase 1: Core Specialist Agents

You will configure Bob modes in `.bob/custom_modes.yaml` and operating instructions in `.bob/skills/<name>/SKILL.md`:

| Role | Mode Slug | What it does |
|---|---|---|
| **PM Agent** | `pm-agent` | Analyzes feature request, checks out `feature/<slug>` branch, writes User Stories & Acceptance Criteria |
| **Architect Agent** | `architect-agent` | Reads PM analysis, designs DB schema, API contracts, frontend architecture, and writes an Engineer Checklist |
| **Engineer Agent** | `engineer-agent` | Implements the code changes in Flask & React, writes backend tests, and runs `uv run pytest` |
| **Reviewer Agent** | `reviewer-agent` | **Read-only**; reviews changed code against Acceptance Criteria and issues a verdict (`Approved` / `Changes Required`) |

### Key Design Rules:
- Agents communicate **only** through the workflow document (`feature-workflows/<feature>-workflow.md`) — no external databases or complex message queues.
- Each agent reads what previous agents wrote and appends its own section.
- The `current-role` field in the document's YAML front matter tracks which agent acts next.
- The Reviewer Agent is strictly read-only on application source code (enforced by `fileRegex` write restriction in `.bob/custom_modes.yaml`).

---

## Step 5 — Run the Feature Pipeline

Pick a feature request (e.g. [`feature-requests/add-priorities.md`](../feature-requests/add-priorities.md)) and run the workflow by switching modes:

1. **PM Agent Mode** (`pm-agent`):
   ```text
   Please analyze the feature request at feature-requests/add-priorities.md and create the workflow document.
   ```
2. **Architect Agent Mode** (`architect-agent`):
   ```text
   Please design the implementation for feature-workflows/add-priorities-workflow.md
   ```
3. **Engineer Agent Mode** (`engineer-agent`):
   ```text
   Please implement feature-workflows/add-priorities-workflow.md
   ```
4. **Reviewer Agent Mode** (`reviewer-agent`):
   ```text
   Please review feature-workflows/add-priorities-workflow.md
   ```

*If the Reviewer requests changes (`Changes Required`), switch back to Engineer Agent and run:*
```text
Please address the review feedback in feature-workflows/add-priorities-workflow.md
```

---

## Step 6 — Build Phase 2: SDLC Orchestrator Agent

Once Phase 1 is tested, build the **SDLC Orchestrator Agent** following [`orchestrator_agent_spec.md`](../orchestrator_agent_spec.md).

The Orchestrator mode (`orchestrator-agent`) and skill (`.bob/skills/orchestrator/SKILL.md`) drive the entire PM → Architect → Engineer → Reviewer pipeline automatically with subtasks.

Switch to **SDLC Orchestrator Agent** mode and run:
```text
Please run the full workflow for feature-requests/add-priorities.md
```

---

## Feature Catalogue

| File | Feature | Complexity | Recommended For |
|---|---|---|---|
| `add-priorities.md` | **Priorities** | ⭐ Low | First demo / workshop run |
| `add-due-dates.md` | **Due Dates** | ⭐⭐ Low–Medium | Date logic & overdue UI styling |
| `add-search.md` | **Search & Filter** | ⭐⭐ Medium | Pure frontend filtering & state |
| `add-tags.md` | **Tags / Labels** | ⭐⭐ Medium | Many-to-many database relationships |
| `kanban-board.md` | **Kanban Board** | ⭐⭐⭐ Medium–High | Full multi-column view & state mapping |
| `analytics-dashboard.md` | **Analytics** | ⭐⭐⭐ High | Aggregation endpoints & charting |

---

## Troubleshooting

| Issue | Cause & Fix |
|---|---|
| `use_skill` returns "skill not found" | Bob indexes skills at conversation start. **Close the current chat and open a new Bob conversation.** |
| `uv run pytest` fails with "command not found" | Install `uv` via `brew install uv` (macOS) or `pip install uv`. |
| Tests fail with "no such column" | Delete `todo-app/backend/todos.db` — SQLite will recreate it with the latest schema on startup. |
| Reviewer Agent cannot modify `.py` or `.jsx` files | This is intentional! The Reviewer mode is restricted to editing only workflow markdown documents. |
| Newly added custom modes not showing up | Ensure `.bob/custom_modes.yaml` is valid YAML and restart your Bob conversation/editor. |
