# Watch Party Demo Script — Building an Agentic SDLC Workflow with Bob

> **Facilitator guide.** Read everything in `>` blockquotes aloud or paraphrase.
> Steps labelled **[PARTICIPANT]** are things every participant does on their own machine.
> Steps labelled **[FACILITATOR]** are screen-share demonstrations.
> Callout boxes like `⚠️ Bob might ask you to...` warn about non-deterministic moments where Bob may behave differently for different participants.

---

## Before the Session (T−15 min)

### Participants: Choose your path

There are two ways to follow along. Both paths reach the same end state.

| | Path A — Full GitHub Integration | Path B — Markdown Only |
|---|---|---|
| **What you need** | GitHub account + fork + PAT | Nothing extra |
| **What you get** | Real Issues, real PRs | Workflow docs only |
| **Recommended for** | Engineers comfortable with git | Everyone else / first-timers |

---

## Path A Setup — GitHub Integration

> "If you want full GitHub integration — real Issues and PRs — do this setup now. If you are going the Markdown-only route, skip to Path B Setup."

### Step A1 — Fork the repository

1. Go to: **https://github.com/tschechlovdev/watch-party-building-ai-agents**
2. Click **Fork** (top right) → keep all defaults → **Create fork**
3. Clone your fork:
   ```bash
   git clone git@github.com:<YOUR_USERNAME>/watch-party-building-ai-agents.git
   cd watch-party-building-ai-agents
   git checkout -b enhancement
   ```

### Step A2 — Create a GitHub Personal Access Token (PAT)

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. Set:
   - **Token name**: `bob-watch-party`
   - **Expiration**: 7 days (or 1 day for extra safety)
   - **Repository access**: Only select repositories → choose your fork
   - **Repository permissions**:
     - **Issues**: Read and write
     - **Pull requests**: Read and write
     - **Contents**: Read and write (needed if Engineer pushes via Bob)
     - **Metadata**: Read (required, auto-selected)
4. Click **Generate token** — **copy it now**, it is shown only once

### Step A3 — Add the GitHub MCP server to Bob

Open `.bob/mcp.json` in your workspace and add the `github` entry:

```json
{
  "mcpServers": {
    "bob-marketplace": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:39247/mcp",
      "headers": { "Bob-Marketplace-Token": "bob-marketplace-local" },
      "disabled": false,
      "alwaysAllow": [
        "search_assets", "get_asset", "list_installed",
        "list_favorites", "suggest_assets", "list_updates"
      ]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_PAT_HERE>"
      },
      "disabled": false
    }
  }
}
```

> ⚠️ **Never commit this file with the PAT in it.** Add `.bob/mcp.json` to your `.gitignore`, or replace the literal PAT with an environment variable reference (see below).

**Safer alternative — read the PAT from an environment variable:**

```json
"env": {
  "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
}
```

Then export the variable before starting Bob:
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Step A4 — Restart Bob

Reload the Bob window (or restart your editor) so Bob picks up the new MCP server.

Verify it is connected: open a new Bob conversation and type:
```
List my GitHub repos
```
Bob should respond with your repositories using the GitHub MCP tools.

---

## Path B Setup — Markdown Only

> "Nothing to install. Open the project in Bob and you are ready."

**[PARTICIPANT]**
1. Open the `watch_party_building_ai_agents/` folder in Bob (or your editor with Bob)
2. Confirm the backend works:
   ```bash
   cd todo-app/backend
   uv run pytest
   # Should show: 31 passed
   ```

That is all. You will run the full workflow and produce a real code change. The only thing you won't do automatically is open a GitHub Issue or PR — you can do that manually at the end if you want.

---

## Session Start (T+0)

> "Welcome. Today we are going to build an agentic software development lifecycle — a mini development team made of Bob modes — and use it to ship a real feature into a real Todo application. By the end of the session you will have seen PM analysis, architecture design, implementation, and code review all happen inside Bob, coordinated by a single markdown document."

> "We are building this incrementally across two phases. Today covers **Phase 1 — the core agents**: PM, Architect, Engineer, and Reviewer. Each runs as a separate Bob mode and hands off via a shared workflow document. Phase 2 — the Orchestrator — is a single-prompt driver that runs all of those automatically; we will cover that separately."

---

## Part 1 — What Are We Building? (5 min)

> "Let me show you the structure."

**[FACILITATOR]** Open `sdlc_agents_spec.md` and walk through:
- The two-phase build: core agents first, Orchestrator later
- The four agent roles (PM → Architect → Engineer → Reviewer)
- The PM Agent's first responsibility: create a local git feature branch before writing anything

Then open `docs/NOTES.md` and walk through:
- The shared handoff document (`feature-workflows/`)
- The feature request catalogue (`feature-requests/`)

> "The key idea: no orchestration framework, no inter-process communication. Every agent reads the document, appends its section, and sets a `current-role` field in the front matter to signal who goes next. That's it. The Orchestrator we'll show later simply automates those manual mode switches — but the core workflow is fully functional without it."

---

## Part 2 — Pick a Feature (2 min)

> "We are going to run the **Priorities** feature — it is the simplest one and completes in about 20 minutes. If you want a harder challenge, try Due Dates or Search."

**[PARTICIPANT]**  
Open `feature-requests/add-priorities.md` and read it. This is your feature request.

---

## Part 3 — PM Agent (5–8 min)

**[PARTICIPANT]**

1. Switch Bob to **PM Agent** mode (mode switcher, top of the chat)
2. Type:
   ```
   Please analyze the feature request at feature-requests/add-priorities.md
   and create the workflow document for it.
   ```

> ⚠️ **Bob might ask you** which workflow document filename to use — answer: `feature-workflows/add-priorities-workflow.md`

> ⚠️ **Bob might ask you** whether to create the workflow document from the template — answer: yes

**What Bob will do (deterministically from the skill):**
- Read `feature-requests/add-priorities.md`
- Read `models.py`, `routes.py`, `App.jsx` for context
- Create `feature-workflows/add-priorities-workflow.md` from the template
- Fill in `## PM Analysis` with User Stories, Acceptance Criteria, Out of Scope
- Set `current-role: architect`
- Tell you to switch to Architect mode

**[FACILITATOR]** Show the filled workflow document. Point out:
- The user stories are behavioural — no mention of columns or API endpoints
- The acceptance criteria are checkboxes — concrete and testable
- The hint comments are still there (guidance for agents, not output)

---

## Part 4 — Architect Agent (5–8 min)

**[PARTICIPANT]**

1. Switch Bob to **Architect Agent** mode
2. Type:
   ```
   Please design the implementation for feature-workflows/add-priorities-workflow.md
   ```

> ⚠️ **Bob might ask you** to confirm which files to read — just say "go ahead" or "read all of them"

**What Bob will do:**
- Read the workflow document (PM Analysis)
- Read `models.py`, `routes.py`, `api.js`, `App.jsx`
- Fill in `## Architecture Design` with DB schema, API changes, frontend changes, engineer checklist, open questions
- Set `current-role: engineer`

**[FACILITATOR]** Show the Architecture Design section. Key talking points:
- "The Architect never writes code — only descriptions and a numbered checklist"
- "The Open Questions section is how the Architect flags edge cases for the Engineer without making the decision for them"
- "This minimal design is what keeps the Engineer from gold-plating"

---

## Part 5 — Engineer Agent, First Pass (10–15 min)

**[PARTICIPANT]**

1. Switch Bob to **Engineer Agent** mode
2. Type:
   ```
   Please implement feature-workflows/add-priorities-workflow.md
   ```

> ⚠️ **Bob might ask you** whether to proceed with all file changes at once — say yes

> ⚠️ **Bob might ask you** which Python environment to use for pytest — say:
> ```
> Use: cd todo-app/backend && uv run pytest
> ```

**What Bob will do:**
- Detect this is the first pass (Review Feedback section is empty)
- Read the Architecture Design checklist
- Implement all backend and frontend changes
- Write tests
- Run `uv run pytest` — fix failures if any
- Fill in `## Implementation Notes`
- Set `current-role: reviewer`

**[FACILITATOR]** While it runs, talk through:
- "The Engineer skill has a pass detection step — it reads the Review Feedback section to decide whether this is a first or second pass. No extra prompt needed."
- "The guardrails prevent it from adding features the Architect didn't spec — minimal change only."

---

## Part 6 — Reviewer Agent (5–8 min)

**[PARTICIPANT]**

1. Switch Bob to **Reviewer Agent** mode
2. Type:
   ```
   Please review feature-workflows/add-priorities-workflow.md
   ```

**What Bob will do:**
- Read the entire workflow document
- Read every file listed in Implementation Notes > Files Changed
- Check: correctness vs acceptance criteria, test coverage, security, API contract, code style
- Fill in `## Review Feedback` with Blocking Issues and Suggestions
- Set verdict: **Approved** or **Changes Required**

> ⚠️ **If verdict is Approved:** the workflow is done. Go to Part 7.

> ⚠️ **If verdict is Changes Required:** switch back to Engineer Agent mode and type:
> ```
> Please address the review feedback in feature-workflows/add-priorities-workflow.md
> ```
> The Engineer skill detects the second pass automatically and fills `## Improvement Notes`.
> Then switch to Reviewer Agent again for final sign-off.

**[FACILITATOR]** Talking point:
- "The Reviewer can't fix code — it can only write feedback. That constraint is enforced by the mode's `fileRegex` write restriction. This mimics a real PR review where the reviewer comments but the author applies the fix."

---

## Part 7 — GitHub Integration (Path A only) (3–5 min)

> "If you are on Path A, let's now wire the result to GitHub."

**[PARTICIPANT — Path A]**

After the Reviewer approves, stay in any mode and type:

```
1. Create a GitHub issue in my fork for this feature request
   using the content of feature-requests/add-priorities.md
2. Commit all changes, push to the enhancement branch, and open a PR
   that references the issue you just created
```

> ⚠️ **Bob might ask you** to confirm the repository name — provide: `<YOUR_USERNAME>/watch-party-building-ai-agents`

> ⚠️ **Bob might ask you** for a PR title and description — you can say "generate a good one from the workflow document"

> ⚠️ **Bob might ask you** whether to push via git commands or the GitHub MCP server — either works; `git push` + `gh pr create` via shell is the most reliable

**What Bob will do (using GitHub MCP tools):**
- Call `create_issue` with the feature request content and `enhancement` label
- Run `git add . && git commit && git push`
- Call `create_pull_request` with `Closes #<issue number>` in the body
- Return the PR URL

**[PARTICIPANT — Path B]**

You can do this manually:
1. Push your branch: `git push origin enhancement`
2. Open a PR on GitHub at: `https://github.com/tschechlovdev/watch-party-building-ai-agents/compare/main...enhancement`
3. Reference the Kanban Board issue in the PR body: `Closes #2`

---

## Part 8 — Reflection (5 min)

> "Let's talk about what just happened."

**Discussion prompts:**

1. **Where did Bob make decisions vs. follow instructions?**  
   The skills are deterministic step-by-step instructions. Bob's non-determinism shows up in *how* it phrases things, *which files* it chooses to read for context, and *whether it asks a clarifying question* at ambiguous moments.

2. **Where did Bob ask a question — and could we have prevented it?**  
   Most clarifying questions happen when the input is ambiguous (e.g. "which workflow file?"). Writing more specific prompts ("use `feature-workflows/add-priorities-workflow.md`") eliminates most of them.

3. **What would break if you ran this on a different feature?**  
   The skills reference specific file paths (`todo-app/backend/models.py` etc.). A different application would need updated skills. The *workflow structure* (PM → Architect → Engineer → Reviewer) is application-agnostic.

4. **What's missing from this workflow?**  
   - Parallelism (e.g. running tests while the Reviewer reads)
   - Automated handoff (a Bob hook could trigger the next agent automatically)
   - Security review agent
   - Frontend tests

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `use_skill` returns "skill not found" | Skills created in the same session aren't visible yet. Start a new Bob conversation. |
| `uv run pytest` fails with "command not found" | Run `pip install uv` or `brew install uv`, or replace with `python -m pytest` |
| Tests fail with "no such column: status" | Delete `todo-app/backend/todos.db` and re-run — the migration will rebuild it |
| GitHub MCP not connecting | Check `mcp.json` syntax; verify the PAT has Issues + PRs + Contents permissions; restart Bob |
| PAT accidentally committed | Rotate it immediately at GitHub → Settings → Developer settings → Personal access tokens |
| Bob ignores the skill instructions | Confirm the mode's `customInstructions` says `use_skill tool with skill_name "..."` and that the skill file exists at `.bob/skills/<name>/SKILL.md` |
| Reviewer mode can't edit source files | That's by design — the `fileRegex` write restriction is intentional |

---

## What's Next

| Extension | How |
|---|---|
| **Phase 2 — SDLC Orchestrator Agent** | Switch to **SDLC Orchestrator Agent** mode and send a single feature request — it drives PM → Architect → Engineer → Reviewer automatically as subtasks. Spec: `orchestrator_agent_spec.md` |
| **Run a second feature** | Pick any file from `feature-requests/` and repeat Parts 3–7 |
| **Add a Security Review agent** | Add a new mode + skill that reads Implementation Notes and checks the security checklist from the project rules |
| **Automate handoffs with Bob hooks** | Use Bob's lifecycle hooks to auto-trigger the next agent on session end |
| **Subagent parallelism** | Use `spawn_subagent` in the Engineer skill to run tests in parallel with documentation |
| **Adapt to your own project** | Update the skill files to reference your app's file paths and tech stack |
