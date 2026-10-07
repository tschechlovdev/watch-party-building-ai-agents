# Building an Agentic SDLC Workflow with Bob

A hands-on watch-party project that demonstrates how to build an autonomous AI development team inside [IBM Bob](https://bob.ibm.com) — **PM**, **Architect**, **Engineer**, and **Reviewer** — coordinated purely through a shared markdown document, with **no external orchestration frameworks, vector databases, or complex infrastructure required**.

The workflow takes a raw feature request and autonomously designs, implements, tests, and reviews real code changes in a full-stack Todo application (Flask backend + React frontend).

---

## The Premise & Mental Model

### Why an Agentic SDLC Team?
In traditional software development, shipping a quality feature requires distinct perspectives:
1. **Product Management (PM)**: Clarifies user value, acceptance criteria, and scopes boundaries (*"What to build and why"*).
2. **Architecture**: Designs DB schema migrations, API contracts, and component hierarchy (*"How to structure it cleanly"*).
3. **Engineering**: Implements code, writes tests, and runs local test suites (*"Writing working, verified code"*).
4. **Code Review**: Performs an objective, read-only quality and security check against the acceptance criteria (*"Verification & gatekeeping"*).

Instead of asking a single prompt to do everything at once (which often misses edge cases or skips testing), Bob allows you to configure **specialized agent personas** (Modes + Skills).

### Shared Memory via Markdown (No Complex Orchestrator Needed)
Most multi-agent frameworks require external servers, message queues, or Python orchestration libraries. In this project:
- **A single markdown document (`feature-workflows/<feature>-workflow.md`) acts as the shared state and memory.**
- Each agent reads what previous agents wrote, appends its own structured section, updates the `current-role` front matter, and hands off to the next role.

```text
Feature Request (.md or GitHub Issue)
    ↓
PM Analysis (User Stories & Acceptance Criteria + Git Feature Branch)
    ↓
Architecture Design (DB Schema, API Contracts, Frontend Plan)
    ↓
Implementation (Flask + React Code, Tests, Pytest execution)
    ↓
Code Review (Read-only check against Acceptance Criteria)
    ↓
[Approved] → Pull Request / Merge
[Changes Required] → Engineer 2nd pass → Reviewer
```

---

## Repository Structure & File Guide

### What is in this repository?

```text
.
├── docs/
│   └── INSTRUCTIONS.md          # 📖 Step-by-step lab guide for workshop participants
│
├── sdlc_agents_spec.md          # 📋 Phase 1 Specification: Core 4 agents & handoff design
├── orchestrator_agent_spec.md   # 📋 Phase 2 Specification: Automated pipeline driver
│
├── templates/
│   └── feature-workflow.md      # 📝 Blank handoff template copied for every new feature
│
├── feature-requests/            # 💡 Ready-to-use feature ideas of varying complexity
│   ├── add-priorities.md        # ⭐ Low: Priority badges & sorting (Recommended first demo)
│   ├── add-due-dates.md         # ⭐⭐ Low-Med: Date handling & overdue styling
│   ├── add-search.md            # ⭐⭐ Med: Client-side search & filtering
│   ├── add-tags.md              # ⭐⭐ Med: Tagging system (Many-to-many DB pattern)
│   ├── kanban-board.md          # ⭐⭐⭐ Med-High: Multi-column board view
│   └── analytics-dashboard.md   # ⭐⭐⭐ High: Metrics API + chart visualization
│
├── feature-workflows/           # 📂 Target directory where active & completed feature workflows live
│
├── todo-app/                    # 🚀 The application under development
│   ├── backend/                 # Flask 3 + SQLite database + pytest test suite
│   └── frontend/                # React 19 + Vite + Tailwind CSS
│
└── .bob/                        # 🤖 Agent Configuration (Built in Phase 1 & 2)
    ├── custom_modes.yaml        # Agent modes (pm-agent, architect-agent, engineer-agent, reviewer-agent, orchestrator)
    └── skills/                  # Detailed instructions for each agent role
        ├── pm/SKILL.md
        ├── architect/SKILL.md
        ├── engineer/SKILL.md
        ├── reviewer/SKILL.md
        └── orchestrator/SKILL.md
```

> ℹ️ **Note on `.bob/`**: In the `main` starter branch, you build `.bob/custom_modes.yaml` and the skills during Phase 1 & 2 following [`docs/INSTRUCTIONS.md`](docs/INSTRUCTIONS.md). If you want to inspect a pre-completed, ready-to-run setup, check out the `origin/sdlc-agents-solution` branch.

---

## Getting Started

### 1. Prerequisites
| Tool | Purpose |
|---|---|
| [IBM Bob](https://bob.ibm.com) | Running the AI agent workflow |
| Python 3.11+ with [`uv`](https://github.com/astral-sh/uv) | Running backend tests (`uv run pytest`) |
| Node.js 18+ | Running the React frontend dev server |
| Git | Version control & branching |

---

### 2. Clone and Open in Bob

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tschechlovdev/watch-party-building-ai-agents.git
   cd watch-party-building-ai-agents
   ```

2. **Verify backend tests pass:**
   ```bash
   cd todo-app/backend
   uv run pytest
   # Expected: 17 passed
   cd ../..
   ```

3. **Open the Project in IBM Bob:**
   * Open the IBM Bob desktop application (or Bob inside VS Code).
   * In the top menu, go to **File → Open Folder...** (or press `Cmd+O` on macOS / `Ctrl+O` on Windows/Linux).
   * Select the root **`watch-party-building-ai-agents`** folder.

---

## How to Run the Workflow

You can run the workflow in two ways:

### Option A: Specialist Modes (Phase 1 — Recommended to learn the mechanics)

Switch Bob's mode dropdown at the bottom of the chat for each step:

#### Step 1 — PM Agent (`pm-agent`)
* **Prompt:**
  ```text
  Please analyze the feature request at feature-requests/add-priorities.md
  and create the workflow document for it.
  ```
* **What happens:** The PM creates a git feature branch (`feature/add-priorities`), initializes `feature-workflows/add-priorities-workflow.md`, writes User Stories & Acceptance Criteria, and specifies whether an Architect phase is needed (`needs-architect: true`).

#### Step 2 — Architect Agent (`architect-agent`)
* **Prompt:**
  ```text
  Please design the implementation for feature-workflows/add-priorities-workflow.md
  ```
* **What happens:** The Architect inspects the codebase and fills in the DB schema changes, API endpoint signatures, frontend component adjustments, and an ordered Engineer Checklist.

#### Step 3 — Engineer Agent (`engineer-agent`)
* **Prompt:**
  ```text
  Please implement feature-workflows/add-priorities-workflow.md
  ```
* **What happens:** The Engineer modifies `models.py`, `routes.py`, and React components, adds backend test cases in `tests/test_routes.py`, runs `uv run pytest` until all tests pass, and documents the implementation notes.

#### Step 4 — Reviewer Agent (`reviewer-agent`)
* **Prompt:**
  ```text
  Please review feature-workflows/add-priorities-workflow.md
  ```
* **What happens:** The Reviewer is **read-only** (cannot edit source files). It evaluates the changes against the acceptance criteria and issues a verdict:
  * **Approved** → Feature is ready! Merge branch or create a PR.
  * **Changes Required** → Switch back to Engineer Agent and run:
    ```text
    Please address the review feedback in feature-workflows/add-priorities-workflow.md
    ```

---

### Option B: SDLC Orchestrator Agent (Phase 2 — Full Automation)

If you have configured Phase 2 ([`orchestrator_agent_spec.md`](orchestrator_agent_spec.md)), you don't need to manually switch modes between steps.

Switch to **SDLC Orchestrator Agent** mode and send a single prompt:
```text
Please run the full workflow for feature-requests/add-priorities.md
```
The Orchestrator will automatically trigger PM, Architect, Engineer, and Reviewer as sequential subtasks and report the final result.

---

## Optional: GitHub Integration (Issues & PRs)

To connect the agent workflow directly to GitHub:

1. Create a GitHub Personal Access Token (PAT) with `repo`, `issues`, and `pull-requests` permissions.
2. Export your token:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```
3. Add the GitHub MCP server to `.bob/mcp.json`:
   ```json
   {
     "mcpServers": {
       "github": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
         }
       }
     }
   }
   ```
4. Now the PM agent can read live GitHub issues, and the workflow can create real Pull Requests on completion.

---

## Bonus: Parallel Feature Swarms with Git Worktrees

Want to run multiple AI feature pipelines simultaneously on the same codebase without collisions? Use **Git Worktrees**:

```bash
# Create isolated worktree folders for different features
git worktree add ../watch-party-due-dates  -b feature/add-due-dates
git worktree add ../watch-party-search     -b feature/add-search
git worktree add ../watch-party-tags       -b feature/add-tags
```

Open each folder in a separate Bob window (**File → Open Folder**). Run an Orchestrator agent in each window simultaneously. All pipelines execute concurrently on their own branches!

---

## Further Resources & Next Steps
* Detailed lab guide: [`docs/INSTRUCTIONS.md`](docs/INSTRUCTIONS.md)
* Core agent specifications: [`sdlc_agents_spec.md`](sdlc_agents_spec.md)
* Orchestrator specification: [`orchestrator_agent_spec.md`](orchestrator_agent_spec.md)
* Extensions & ideas for going further: [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md)
