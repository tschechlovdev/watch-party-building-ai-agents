# Building AI Agent Development Team — Documentation Journal

## About This Document

This file is the running documentation journal for the **watch-party session on building an Agentic SDLC workflow with Bob**.

The session demonstrates how Bob can support a complete software development lifecycle — from a plain-text feature request, through product analysis and architecture design, to code implementation and review — using only Bob modes, skills, and a shared markdown document as the coordination layer.

Every sub-task in the implementation plan appends to this file. If you are following along at a watch party, this document is your map: it tells you what was built, why each decision was made, what worked well, what did not, and what you would need to go further (such as GitHub integration).

**Useful tip from setup:**  
Internet access via the fetch MCP server can be added with:
```
npx -y mcp-fetch-server --help
```

---

## Architecture

### Mode + Skill Approach

Each agent role in the workflow is implemented as a **Bob mode** paired with a **Bob skill**:

- The **mode** (`custom_modes.yaml`) defines the agent's persona, scopes its tool access, and optionally auto-loads its skill.
- The **skill** (`.bob/skills/<role>/SKILL.md`) contains the agent's detailed operating instructions: what to read, what to write, what format to produce, and what guardrails to respect.

This separation keeps personas and permissions at the mode level while keeping task-specific logic in the skill — making it easy to update either independently.

### Shared Handoff Document

All agents communicate through a single living document: `feature-workflow.md`. Rather than inter-process messaging or a database, each agent reads the sections written by previous agents and appends its own section. The document moves through the following stages:

```
Feature Request → PM Analysis → Architecture Design → Implementation Notes → Review Feedback → Improvement Notes → Final Status
```

This file is the only shared memory between agent roles. No external orchestration layer is required.

### Design Principles (from `enhancement_spec.md`)

- Focus on working end-to-end workflows.
- Prefer simplicity over sophistication.
- Keep components loosely coupled.
- Design for extensibility — additional agents should be easy to add.
- Make it easy to replace individual agents.
- Avoid framework-specific assumptions where possible.

---

## Setup Requirements

To run this workflow you need:

| Requirement | Detail |
|---|---|
| **Bob** | Latest version with modes and skills support |
| **Custom modes** | `.bob/custom_modes.yaml` must exist in the workspace |
| **Skills directory** | `.bob/skills/` must be present; each skill lives at `.bob/skills/<name>/SKILL.md` |
| **Workspace** | Project root: `watch_party_building_ai_agents/` |
| **Todo app** | Flask backend at `todo-app/backend/`, React+Vite frontend at `todo-app/frontend/` |
| **Python runtime** | `uv` for running backend tests (`uv run pytest`) |
| **Node.js** | Required for the Vite frontend dev server |

No GitHub account, token, or CLI tool is required to run the core workflow. GitHub integration is a future step (see [Future Requirements](#future-requirements)).

---

## Agent Roles

| Role | Mode slug | Skill | Responsibility |
|---|---|---|---|
| **PM** | `pm-agent` | `.bob/skills/pm/SKILL.md` | Reads a feature request; writes User Stories, Acceptance Criteria, and Out-of-Scope items into the workflow document. Does not touch source code. |
| **Architect** | `architect-agent` | `.bob/skills/architect/SKILL.md` | Reads the PM Analysis and the existing codebase; writes DB schema changes, API changes, frontend changes, and an engineer checklist into the workflow document. No code. |
| **Engineer** | `engineer-agent` | `.bob/skills/engineer/SKILL.md` | Implements the Architecture Design; writes backend tests; fills in Implementation Notes. On a second pass (if reviewer requests changes), addresses Review Feedback and fills in Improvement Notes. The single mode handles both passes via pass detection. |
| **Reviewer** | `reviewer-agent` | `.bob/skills/reviewer/SKILL.md` | Reads the implementation and all changed files; checks correctness, tests, security, API contract, and style; writes Review Feedback with a verdict (Approved / Changes Required). Read-only — never modifies source code. |

### Tool Access per Role

| Role | File reads | File writes | Shell execution |
|---|---|---|---|
| PM | All files | `feature-workflows/*.md`, `docs/*.md` | No |
| Architect | All files | `feature-workflows/*.md`, `docs/*.md` | No |
| Engineer | All files | All files | Yes (for running pytest) |
| Reviewer | All files | `feature-workflows/*.md`, `docs/*.md` | No |

---

## Workflow Overview

To run a feature through the SDLC workflow:

1. **Write a feature request** — create a plain markdown file in `feature-requests/` describing what you want built. See the catalogue in `feature-requests/` for ready-made examples.
2. **Copy the template** — copy `templates/feature-workflow.md` to `feature-workflows/<feature-name>-workflow.md`.
3. **Activate PM mode** (`pm-agent`) — paste or reference the feature request; the PM fills in `## PM Analysis` (user stories, acceptance criteria, out of scope).
4. **Activate Architect mode** (`architect-agent`) — the Architect reads the PM Analysis and the existing codebase, then fills in `## Architecture Design` (schema, API, frontend changes, engineer checklist).
5. **Activate Engineer mode** (`engineer-agent`) — the Engineer implements the Architecture Design, runs `uv run pytest`, and fills in `## Implementation Notes`.
6. **Activate Reviewer mode** (`reviewer-agent`) — the Reviewer reads the entire workflow document and the changed files, then fills in `## Review Feedback` with a verdict (Approved / Changes Required).
7. **If Changes Required** — re-activate Engineer mode; the skill detects the second pass from the filled Review Feedback section and fills in `## Improvement Notes`.
8. **Final Status** — once approved, the outcome is recorded. A PR reference is a placeholder for future GitHub integration.

### Template Structure

The blank template lives at `templates/feature-workflow.md`. It contains hint comments (HTML `<!-- ... -->` blocks) in each section guiding the agent on what to write.

The `current-role` field in the YAML front matter tracks which agent acts next:

| Value | Meaning |
|---|---|
| `pm` | PM Agent turn |
| `architect` | Architect Agent turn |
| `engineer` | Engineer Agent turn (first or second pass) |
| `reviewer` | Reviewer Agent turn |
| `done` | Workflow complete |

The `feature-workflows/` directory holds one filled-in workflow document per feature that has been run end-to-end.

---

## Feature Request Catalogue

The `feature-requests/` directory contains pre-written feature requests you can use to drive the
workflow. Choose one based on the complexity you want to demonstrate:

| File | Feature | Complexity | What it touches |
|---|---|---|---|
| `add-priorities.md` | **Priorities** | Low | +1 DB column, filter param, UI badge — **recommended for first demo** |
| `add-tags.md` | **Tags / Labels** | Low–Medium | Many-to-many table, tag CRUD endpoints, UI chips |
| `add-due-dates.md` | **Due Dates** | Low–Medium | +1 DB column, date input, overdue highlighting |
| `add-search.md` | **Search & Filter** | Medium | No schema change, client-side filtering, search bar UI |
| `kanban-board.md` | **Kanban Board** | Medium–High | Status column, grouped board view, move-card UI |
| `analytics-dashboard.md` | **Analytics Dashboard** | High | Aggregation API, chart component, read-only view |

To run any feature, copy `templates/feature-workflow.md` to
`feature-workflows/<feature-name>-workflow.md`, then activate the agent roles in sequence.

---

## What Works

_This section will be populated during the demo run._

---

## Known Limitations

_This section will be populated during the demo run (Sub-Task 7)._

---

## Future Requirements

### GitHub Integration

The current workflow produces code changes directly in the repository but does not open a GitHub Issue or create a Pull Request automatically. The full intended flow from `enhancement_spec.md` ends with:

```
Improved Implementation → Pull Request → Merge
```

Enabling this final step requires one of the following:

- **GitHub MCP server** — connects Bob to the GitHub API so it can create issues and open PRs as tool calls within any mode. This is the preferred approach for a seamless in-session experience.
- **`gh` CLI** — the official GitHub CLI; allows Bob's engineer or reviewer mode to run `gh pr create` via shell execution tools after the implementation is complete.

This is a **planned next step** after the core workflow is validated end-to-end. It is listed as a non-goal in the current implementation plan and should be treated as an enhancement once the PM → Architect → Engineer → Reviewer loop is stable.

Other potential future extensions (from `enhancement_spec.md`):

- Subagents for parallelising tasks (e.g. running tests while the reviewer reads code)
- Bob hooks for automating handoff triggers
- Security review agent
- Testing agent
- UI generation agent
- Enterprise deployment patterns
