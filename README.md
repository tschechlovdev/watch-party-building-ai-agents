# Building an Agentic SDLC Workflow with Bob

A watch-party project that demonstrates how to build a mini AI development team inside [IBM Bob](https://bob.ibm.com) — PM, Architect, Engineer, and Reviewer — coordinated by a single markdown document, with no orchestration framework required.

The workflow ships a real feature into a real Todo application (Flask backend + React frontend) end-to-end.

The project is built **incrementally in two phases**:

| Phase | Spec | What it adds |
|---|---|---|
| **Phase 1 — Core agents** | [`sdlc_agents_spec.md`](04%20Workspace/watch_party_building_ai_agents%202026-10-15/sdlc_agents_spec.md) | PM · Architect · Engineer · Reviewer, handoff document, feature branch creation |
| **Phase 2 — SDLC Orchestrator** | [`orchestrator_agent_spec.md`](04%20Workspace/watch_party_building_ai_agents%202026-10-15/orchestrator_agent_spec.md) | Single-prompt pipeline driver that runs all agents automatically as subtasks |

Start with Phase 1. The core agents work standalone and are the foundation everything else builds on.

> 📋 **Workshop participants:** see [`docs/INSTRUCTIONS.md`](04%20Workspace/watch_party_building_ai_agents%202026-10-15/docs/INSTRUCTIONS.md) for the step-by-step setup guide.

---

## How it works

Each agent role is a **Bob mode** paired with a **Bob skill**. The agents hand off to each other through a shared `feature-workflow.md` document:

```
Feature Request → PM Analysis → Architecture Design
    → Implementation → Review → (second pass if needed) → PR
```

No database, no message queue, no external orchestrator. Every agent reads what the previous one wrote and appends its own section.

---

## Repository structure

```
.
├── .bob/
│   ├── custom_modes.yaml           # 5 agent modes: sdlc-orchestrator, pm, architect, engineer, reviewer
│   ├── rules/
│   │   └── agent-setup.md          # Injected into every conversation — setup reminders + fix hints
│   └── skills/
│       ├── orchestrator/SKILL.md   # End-to-end pipeline driver
│       ├── pm/SKILL.md             # PM agent instructions
│       ├── architect/SKILL.md      # Architect agent instructions
│       ├── engineer/SKILL.md       # Engineer agent instructions (handles 1st + 2nd pass)
│       └── reviewer/SKILL.md       # Reviewer agent instructions
├── feature-requests/            # 6 pre-written feature requests (pick one to run)
├── feature-workflows/           # One filled-in workflow doc per completed feature
│   └── kanban-board-workflow.md # Example: complete PM→Architect→Engineer→Reviewer run
├── templates/
│   └── feature-workflow.md      # Blank handoff template — copy this to start a new feature
├── docs/
│   └── NOTES.md                 # Architecture overview, agent roles, GitHub integration guide
└── todo-app/
    ├── backend/                 # Flask 3 + SQLite, pytest
    └── frontend/                # React 19 + Vite + Tailwind CSS
```

---

## Prerequisites

| Tool | Required for |
|---|---|
| [IBM Bob](https://bob.ibm.com) | Running the agent workflow |
| Python 3.11+ with [`uv`](https://github.com/astral-sh/uv) | Backend tests (`uv run pytest`) |
| Node.js 18+ | Frontend dev server |
| Git | Cloning and pushing changes |
| GitHub account + PAT | Path A only — real Issues and PRs (optional) |

---

## Quickstart

### 1. Clone and verify the backend

```bash
git clone https://github.com/tschechlovdev/watch-party-building-ai-agents.git
cd watch-party-building-ai-agents/todo-app/backend
uv run pytest
# Expected: 31 passed
```

### 2. Open the project in Bob

Open the `watch_party_building_ai_agents/` folder as your Bob workspace.

### 3. Pick a feature request

| File | Feature | Complexity | Good for |
|---|---|---|---|
| `add-priorities.md` | **Priorities** | ⭐ Low | First demo — recommended |
| `add-due-dates.md` | **Due Dates** | ⭐⭐ Low–Medium | Date handling + overdue highlighting |
| `add-search.md` | **Search & Filter** | ⭐⭐ Medium | No schema change — pure frontend |
| `add-tags.md` | **Tags / Labels** | ⭐⭐ Medium | Many-to-many DB pattern |
| `kanban-board.md` | **Kanban Board** | ⭐⭐⭐ Medium–High | Already completed — see `feature-workflows/` |
| `analytics-dashboard.md` | **Analytics** | ⭐⭐⭐ High | Aggregation API + charting |

### 4. Run the workflow

For each step, switch Bob to the corresponding mode and send the prompt shown.

#### Step 1 — PM Agent

Switch to **PM Agent** mode, then:
```
Please analyze the feature request at feature-requests/add-priorities.md
and create the workflow document for it.
```

Bob will create `feature-workflows/add-priorities-workflow.md` and fill in user stories, acceptance criteria, and out-of-scope items.

> ⚠️ Bob might ask which workflow filename to use — answer: `feature-workflows/add-priorities-workflow.md`

#### Step 2 — Architect Agent

Switch to **Architect Agent** mode, then:
```
Please design the implementation for feature-workflows/add-priorities-workflow.md
```

Bob will read the codebase and fill in the DB schema, API changes, frontend changes, and an engineer checklist.

> ⚠️ Bob might ask to confirm which files to read — say "go ahead" or "read all of them"

#### Step 3 — Engineer Agent

Switch to **Engineer Agent** mode, then:
```
Please implement feature-workflows/add-priorities-workflow.md
```

Bob will implement all changes, write backend tests, run `uv run pytest`, and fill in Implementation Notes.

> ⚠️ Bob might ask which pytest command to use — answer: `cd todo-app/backend && uv run pytest`

#### Step 4 — Reviewer Agent

Switch to **Reviewer Agent** mode, then:
```
Please review feature-workflows/add-priorities-workflow.md
```

Bob reads every changed file and produces a verdict: **Approved** or **Changes Required**.

- **If Approved** → go to Step 5
- **If Changes Required** → switch back to Engineer Agent and run:
  ```
  Please address the review feedback in feature-workflows/add-priorities-workflow.md
  ```
  The Engineer skill detects the second pass automatically. Then run the Reviewer again.

#### Step 5 — GitHub (optional)

See the [GitHub Integration](#github-integration) section below.

---

## GitHub Integration

There are two paths. Both produce real code changes; only Path A creates GitHub Issues and PRs automatically.

### Path A — Full GitHub Integration

**Requirements:** GitHub account, a fork of this repo, and a Personal Access Token (PAT).

#### Fork the repository

1. Go to **https://github.com/tschechlovdev/watch-party-building-ai-agents**
2. Click **Fork** → **Create fork**
3. Clone your fork and create the working branch:
   ```bash
   git clone git@github.com:<YOUR_USERNAME>/watch-party-building-ai-agents.git
   cd watch-party-building-ai-agents
   git checkout -b enhancement
   ```

#### Create a PAT

GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**

| Setting | Value |
|---|---|
| Token name | `bob-watch-party` |
| Expiration | 7 days |
| Repository access | Only your fork |
| Issues | Read and write |
| Pull requests | Read and write |
| Contents | Read and write |
| Metadata | Read (auto-selected) |

Copy the token — it is shown only once.

#### Add the GitHub MCP server to Bob

Edit `.bob/mcp.json` and add the `github` entry alongside the existing `bob-marketplace` entry:

```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
  },
  "disabled": false
}
```

Export your PAT before starting Bob:
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

> ⚠️ **Never commit a literal PAT.** Always use `${GITHUB_TOKEN}` as an environment variable reference. Consider adding `.bob/mcp.json` to `.gitignore`.

Restart Bob to pick up the new server. Verify with: `List my GitHub repos`

#### After the Reviewer approves

In any Bob mode, type:
```
Create a GitHub issue for this feature request using feature-requests/add-priorities.md,
then commit all changes, push to the enhancement branch, and open a PR referencing the new issue.
```

> ⚠️ Bob might ask to confirm the repository name — provide: `<YOUR_USERNAME>/watch-party-building-ai-agents`

### Path B — Markdown Only

No GitHub account needed. After the Reviewer approves:

```bash
git add .
git commit -m "feat: add priorities"
git push origin enhancement
# Then open a PR manually at github.com if you want
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `use_skill` returns "skill not found" | Bob has not scanned the workspace skills yet — **close this conversation, open a new one**, and try again |
| `uv run pytest` fails with "command not found" | `brew install uv` or `pip install uv` |
| Tests fail with "no such column: status" | Delete `todo-app/backend/todos.db` — it will be recreated with the correct schema |
| GitHub MCP not connecting | Check `mcp.json` syntax; verify PAT permissions; restart Bob |
| PAT accidentally committed | Rotate it immediately at GitHub → Settings → Developer settings → Personal access tokens |
| Reviewer mode can't edit source files | That's by design — the `fileRegex` write restriction is intentional |

---

## What's next

| Extension | How |
|---|---|
| **Phase 2 — SDLC Orchestrator Agent** | Switch to **SDLC Orchestrator Agent** mode and send a single feature request — it drives PM → Architect → Engineer → Reviewer automatically. Spec: [`orchestrator_agent_spec.md`](04%20Workspace/watch_party_building_ai_agents%202026-10-15/orchestrator_agent_spec.md) |
| Run another feature | Pick any file from `feature-requests/` and repeat the workflow |
| Add a Security Review agent | New mode + skill that checks the security checklist from the project rules |
| Automate handoffs | Use Bob lifecycle hooks to trigger the next agent automatically |
| Adapt to your own project | Update the skill files to reference your app's file paths and tech stack |
