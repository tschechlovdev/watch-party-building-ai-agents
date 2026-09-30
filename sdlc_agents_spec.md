# Agentic SDLC Team with Bob

## Goal

Build a minimal but extensible Agentic SDLC workflow around an existing Todo application.

The workflow should demonstrate how Bob can support the software development lifecycle from idea to implementation and review.

The solution should be designed so that additional capabilities can easily be added later.

---

# Core Workflow

```text
Code Base
    ↓
Feature Request
    ↓
Agent Team
    ↓
Implementation
    ↓
Review
    ↓
Improvement
    ↓
Pull Request
    ↓
Merge
```

A possible implementation could look like:

```text
GitHub Issue
    ↓
PM
    ↓
Architect
    ↓
Engineer
    ↓
Reviewer
    ↓
Engineer
    ↓
PR
    ↓
Merge
```

However, the exact responsibilities, interactions and agent architecture should be decided during implementation.

---

# Application

Use the existing Todo application as the foundation.

The AI should propose several possible feature requests that vary in complexity.

Examples:

- Kanban Board
- Team Collaboration
- Priorities
- Tags
- Attachments
- Notifications
- Analytics Dashboard

The implementation should support experimenting with different feature requests.

---

# PM Agent

## Responsibilities

The PM Agent is the first agent to run for any feature. Its responsibilities are:

1. Read and analyze the feature request.
2. **Create a dedicated git feature branch before writing anything.**
3. Read the existing application to understand the current state.
4. Create the workflow document from the template.
5. Write user stories and acceptance criteria.
6. Decide whether an Architect phase is needed.
7. Hand off to the next agent.

## Branch Creation

The PM Agent must create a git feature branch as the very first step after reading the feature
request — before creating or editing any workflow document or application file.

```text
git checkout -b feature/<feature-slug>
```

If the branch already exists (resuming a workflow), switch to it instead:

```text
git checkout feature/<feature-slug>
```

If git is unavailable or the command fails, log a warning and continue — do not block the PM
Analysis on a git failure.

## Feature Selection & Recommendation

When the PM Agent is invoked **without a specific feature request** (no file path, no inline
description, no GitHub issue URL), it must not pick a feature silently. Instead it must:

1. **Discover available work** — in priority order:
   - GitHub MCP or `gh` CLI: list open, unassigned issues from the repository.
   - `feature-requests/` directory: list all `.md` files.

2. **Analyse each candidate** on two dimensions:
   - **Complexity** (Low / Medium / High) — estimated by reading the feature request and
     assessing: number of layers touched (DB, API, frontend), schema migrations required,
     external dependencies, test surface area.
   - **Benefit** (Low / Medium / High) — estimated from: explicit priority/label metadata on
     the issue, keywords such as "urgent", "user-requested", "high-value", or inferred from
     how fundamental the capability is to the application.

3. **Present a ranked recommendation table** to the user:

   | # | Feature | Complexity | Benefit | Recommendation |
   |---|---------|------------|---------|----------------|
   | 1 | Add Priorities | Low | High | ✅ Recommended |
   | 2 | Add Due Dates | Low–Medium | Medium | Good second step |
   | 3 | Add Tags | Medium | Medium | After priorities |
   | … | … | … | … | … |

   Include a one-sentence rationale for the top recommendation.

4. **Ask the user to confirm** which feature to proceed with:
   > "I recommend starting with **[feature name]**. Shall I proceed with this one, or would
   > you like to pick a different feature from the list?"

   Wait for explicit user confirmation. Do not start the PM Analysis, branch creation, or any
   file writes until the user has selected a feature.

---

# Design Principles

- Focus on working end-to-end workflows.
- Prefer simplicity over sophistication.
- Keep components loosely coupled.
- Design for extensibility.
- Make it easy to add additional agents later.
- Make it easy to replace individual agents.
- Avoid framework-specific assumptions where possible.

---

# Evolution Path

The initial version should focus on a working workflow.

Potential future extensions may include:

- Skills
- Subagents
- Feedback loops
- Hooks
- MCP integrations
- GitHub automation
- Security reviews
- Testing agents
- UI generation
- Enterprise deployment

These should be treated as optional extensions rather than initial requirements.

---

# Expected Outcome

At minimum, the system should be able to:

```text
Feature Request
    ↓
Collaborative Agent Workflow
    ↓
Code Changes
    ↓
Review Feedback
    ↓
Improved Implementation
```

Everything else should be considered an enhancement.

---

# GitHub MCP Setup

After building the core agents, ask the user whether they want to configure the **GitHub MCP
server** to enable real GitHub Issues and Pull Requests.

Prompt:

> Would you like to configure the GitHub MCP server so the agents can read GitHub Issues and
> open Pull Requests automatically?
> (You will need a GitHub account and a Personal Access Token with repo + issue + PR permissions.)

**If the user says yes**, guide them through these steps:

1. **Create a PAT** at GitHub → Settings → Developer settings → Personal access tokens →
   Fine-grained tokens. Required permissions: Issues (read/write), Pull requests (read/write),
   Contents (read/write).
2. **Export the token** before starting Bob:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```
3. **Edit `.bob/mcp.json`** and add the `github` entry:
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
4. **Restart Bob** and verify with: `List my GitHub repos`

> ⚠️ Never hardcode a PAT in `.bob/mcp.json`. Always use `${GITHUB_TOKEN}` as an environment
> variable reference.

**If the user says no**, continue without GitHub integration — the agents work fully with local
`feature-requests/` files and git branches.

---

# Guiding Principle

Optimize for working end-to-end workflow first,
extensibility second,
sophistication third.
