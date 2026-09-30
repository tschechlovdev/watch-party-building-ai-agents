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
├── feature-requests/            # pre-written feature requests (pick one to run)
├── feature-workflows/           # one filled-in workflow doc per completed feature
│   └── kanban-board-workflow.md # example: complete PM→Architect→Engineer→Reviewer run
├── templates/
│   └── feature-workflow.md      # blank handoff template — copy this to start a new feature
├── docs/
│   └── INSTRUCTIONS.md          # workshop setup guide
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
# Expected: 17 passed
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

---

## Bonus — "Swarm" of SDLC Agents with git worktrees

Run **multiple features in parallel** — one full PM → Engineer → Reviewer pipeline per worktree, each on its own branch, without interfering with each other.

### Why worktrees?

A normal `git clone` ties you to one checked-out branch at a time. `git worktree` lets you check out additional branches into separate directories, all sharing the same `.git` history. Each Bob conversation opened against a different worktree directory is completely isolated.

### How to set it up

```bash
# From the repo root — create a worktree for each feature you want to run in parallel
git worktree add ../watch-party-due-dates   -b feature/add-due-dates
git worktree add ../watch-party-search      -b feature/add-search
git worktree add ../watch-party-tags        -b feature/add-tags
```

Now open each `../watch-party-<feature>/` folder as a **separate Bob workspace** (File → Open Folder in VS Code, or equivalent). Start an **Orchestrator Agent** conversation in each workspace and send the matching feature request.

All three pipelines run concurrently, write to their own workflow documents, and commit to separate branches. When a pipeline finishes, simply merge its branch back into `main`.

### Clean up finished worktrees

```bash
git worktree remove ../watch-party-due-dates
# repeat for the others
```

---

## Try out things on your own

Once you've run the basic workflow, here are ideas to explore further:

### Add more feature requests

The `feature-requests/` folder is just markdown files — add your own and run the pipeline against them. The only requirement is a clear **Acceptance Criteria** section so the Reviewer has something concrete to check against.

### Add MCP servers

MCP servers give every Bob agent access to external tools. Good candidates for this workflow:

| MCP server | Why it's useful |
|---|---|
| **GitHub MCP** (`@modelcontextprotocol/server-github`) | Issues, PRs, and code search directly in Bob |
| **Jira / Linear MCP** | Pull real tickets as feature requests instead of local files |
| **Sentry / Datadog MCP** | Let the Engineer check whether a change broke anything in production |
| **Postgres / SQLite MCP** | Let the Architect query the live DB schema before designing changes |
| **Slack MCP** | Post the Final Report to a channel when the pipeline finishes |

### Add skills

Skills are markdown instruction files that load into any mode on demand. Ideas:

- **Security Review skill** — checks the [OWASP Top 10](https://owasp.org/www-project-top-ten/) against every changed file; blocks the Reviewer from approving if a critical finding exists.
- **Documentation skill** — generates a `CHANGELOG.md` entry and updates API docs automatically after each approved feature.
- **Test-quality skill** — checks that coverage didn't drop and that every acceptance criterion has a corresponding test.

Public skill repositories (e.g. the [Propel marketplace](https://bob.ibm.com)) are indexed by Bob's marketplace — browse them with `search_assets` or the Bob Marketplace MCP.

### Security and vulnerability scanning

Integrate automated security checks directly into the pipeline:

- Add a **Bob security rule** (already partially in this repo via `global_rules/security.md`) that fires on every code edit.
- Have the Reviewer skill run `bandit` (Python) or `npm audit` (frontend) and include the output in its verdict.
- Add a dedicated **Security Agent** mode that runs between the Engineer and Reviewer — it scans for secrets, outdated dependencies, and known CVEs before the code review happens.

### CI/CD and DevOps agent

Extend the pipeline beyond the PR:

- Add a **CI Agent** mode that watches a GitHub Actions workflow run and reports failures back into the workflow document.
- Add a **Deployment Agent** that triggers a staging deployment after the PR is merged and runs smoke tests.
- Use Bob lifecycle **hooks** (`on_stop`) to automatically push a branch and open a draft PR as soon as the Reviewer approves.

### Other ideas to try

- **Multi-repo support** — point the Engineer Agent at a monorepo and have it touch multiple packages in one pass.
- **Feedback loop agent** — reads closed GitHub issues labelled `bug` and generates regression tests automatically.
- **Changelog agent** — runs after every merge and keeps `CHANGELOG.md` up to date using the workflow documents as input.
- **Load-testing agent** — runs `locust` or `k6` after the Engineer finishes and includes the results in the Reviewer's checklist.
- **Diagram agent** — generates an updated architecture diagram (Mermaid) whenever the DB schema or API surface changes.
