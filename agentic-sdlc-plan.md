# Agentic SDLC Team — Implementation Plan

## Overview

Build a minimal, extensible Agentic SDLC workflow around the existing Todo app using **Bob modes and skills**.

Each agent role (PM, Architect, Engineer, Reviewer) is a dedicated **Bob mode** that auto-loads a matching **Bob skill** containing its detailed operating instructions. A single living **feature-workflow.md** file acts as the shared context document — each role reads it, appends its section, and passes control to the next role. Feature requests start as markdown files. The end result is working code changes in the repo. GitHub PR integration is a future step.

A **NOTES.md** file is maintained throughout to document what works, what does not, and what future requirements (like GitHub API integration) look like — so watch-party participants can follow the same steps.

### Scope
- 4 agent roles: PM, Architect, Engineer, Reviewer
- 4 Bob modes (one per role)
- 4 Bob skills (one per role, auto-loaded by each mode)
- 1 feature-workflow.md template (the shared handoff document)
- 1 `docs/NOTES.md` (documentation journal)
- 1 example feature request markdown file to drive an end-to-end demo

> **Note on the Engineer mode**: There is only one `engineer-agent` mode. The Engineer role is activated twice — first to implement the Architecture Design, then again (if needed) to address Reviewer feedback. The same mode and skill handle both passes; the skill instructions describe how to detect which pass it is on (by checking whether the Review Feedback section is filled in).

### Non-Goals (future)
- GitHub Issue integration
- GitHub PR creation via API
- CI/CD automation
- Security review agent
- Testing agent
- UI generation agent

---

## Sub-Tasks

---

### Sub-Task 1 — Create NOTES.md (Documentation Journal)

**Status**: `[ ] pending`

**Intent**
Establish the documentation journal before anything else. Every sub-task will append to this file. Watch-party participants rely on it to understand what was built, why, what worked, what did not, and what the prerequisites are for future extensions (e.g. GitHub API integration).

**Expected Outcomes**
- `docs/NOTES.md` exists
- Contains a structured template with sections: Overview, Setup, Architecture Decisions, Agent Roles, Workflow, What Works, Known Limitations, Future Requirements (GitHub, etc.)
- Ready to be appended to by subsequent sub-tasks

**Todo List**
1. Create `docs/NOTES.md`
2. Add a header and "About This Document" section explaining the watch-party context
3. Add an "Architecture" section with a brief summary of the mode+skill approach
4. Add a "Setup Requirements" section (Bob version, skills/modes support, workspace config)
5. Add placeholder sections for: Agent Roles, Workflow Overview, What Works, Known Limitations, Future Requirements
6. Add an initial entry under Future Requirements noting that GitHub API integration (Issues, PRs) requires a GitHub MCP server or `gh` CLI and is a planned next step

**Relevant Context**
- Project root: `watch_party_building_ai_agents/`
- `enhancement_spec.md` — use as source of truth for goals, design principles, and evolution path
- `notes.md` — existing one-liner note; fold its content into `docs/NOTES.md`

---

### Sub-Task 2 — Create the Feature Workflow Template

**Status**: `[ ] pending`

**Intent**  
Define the living handoff document that all agent roles read and write. A single `feature-workflow.md` template file captures the full context of a feature request as it moves through PM → Architect → Engineer → Reviewer → Engineer (improvements). Without this, agents have no shared memory of what was decided.

**Expected Outcomes**
- `feature-workflow.md` template exists at project root (or a `templates/` folder)
- Template has clearly delimited sections, one per role, with instructions for what each role must write
- Comments/hints inside each section tell the agent what to produce
- Template is self-explanatory enough for a new participant to understand the intended flow

**Todo List**
1. Create `templates/feature-workflow.md`
2. Add a YAML-style front matter block (feature name, requester, status, current-role)
3. Add a `## Feature Request` section — plain-text description of the desired feature
4. Add a `## PM Analysis` section — acceptance criteria, user stories, out-of-scope items
5. Add a `## Architecture Design` section — backend changes, frontend changes, data model changes, API changes, open questions
6. Add a `## Implementation Notes` section — files changed, approach taken, tests added
7. Add a `## Review Feedback` section — issues found, required changes, approval status
8. Add a `## Improvement Notes` section — how the engineer addressed reviewer feedback
9. Add a `## Final Status` section — outcome, PR reference (placeholder for future GitHub integration)
10. Document the template in NOTES.md under the Workflow Overview section

**Relevant Context**
- `enhancement_spec.md` — Core Workflow and Expected Outcome sections define what each phase produces
- Todo app stack: Flask backend (`todo-app/backend/`), React+Vite frontend (`todo-app/frontend/`)
- The template must be stack-agnostic enough to be reused for any feature request

---

### Sub-Task 3 — Build the PM Mode and Skill

**Status**: `[ ] pending`

**Intent**  
Create the PM (Product Manager) agent role. When activated, this mode reads the feature request, reasons about user value and scope, and writes the `## PM Analysis` section of the workflow document including acceptance criteria and user stories. It is the entry point of the workflow.

**Expected Outcomes**
- `.bob/skills/pm/SKILL.md` exists with PM operating instructions
- PM mode entry in `.bob/custom_modes.yaml` that auto-loads the PM skill
- PM mode has read access to the codebase and write access to the workflow document
- When a user activates PM mode and provides a feature request file, the PM writes its section to the workflow document

**Todo List**
1. Use `use_skill` with `create-skill` to understand SKILL.md schema before writing
2. Create `.bob/skills/pm/SKILL.md` with:
   - Role definition: product manager analyzing feature requests
   - Input: path to a feature request markdown file AND path to the feature-workflow.md
   - Instructions: read the feature request, read the codebase context (stack, existing models), write the PM Analysis section
   - Output format: filled-in `## PM Analysis` section with user stories, acceptance criteria, explicit out-of-scope items, and next role (Architect)
   - Guardrails: do not propose architecture; focus on what, not how
3. Use `use_skill` with `create-mode` to understand custom_modes.yaml schema before writing
4. Add `pm-agent` entry to `.bob/custom_modes.yaml`:
   - roleDefinition: PM role
   - Auto-load the PM skill via `customInstructions` or skill reference
   - Restrict tools to read-only file access + write (for workflow doc)
5. Append a "PM Agent" entry to `docs/NOTES.md` under Agent Roles

**Relevant Context**
- Bob skill location: `.bob/skills/<name>/SKILL.md`
- Bob modes: `.bob/custom_modes.yaml`
- `create-skill` and `create-mode` skills available in Bob marketplace
- Existing `.bob/mcp.json` — do not modify

---

### Sub-Task 4 — Build the Architect Mode and Skill

**Status**: `[ ] pending`

**Intent**  
Create the Architect agent role. It reads the PM's output in the workflow document and the existing codebase, then writes a technical design: which files to change, what the data model changes look like, what API endpoints are needed, and any open questions for the engineer.

**Expected Outcomes**
- `.bob/skills/architect/SKILL.md` exists with Architect operating instructions
- Architect mode entry in `.bob/custom_modes.yaml`
- When activated, the Architect reads the workflow document (especially PM Analysis), reads relevant source files in the Todo app, and fills in the `## Architecture Design` section

**Todo List**
1. Create `.bob/skills/architect/SKILL.md` with:
   - Role definition: software architect translating PM requirements into a technical design
   - Input: feature-workflow.md (reads PM Analysis section)
   - Codebase context to read: `todo-app/backend/models.py`, `todo-app/backend/routes.py`, `todo-app/frontend/src/api.js`, `todo-app/frontend/src/App.jsx`, and relevant component files
   - Instructions: analyze the current data model and API, design minimal changes to support the feature, write the Architecture Design section
   - Output format: filled-in `## Architecture Design` section with DB schema changes, new/modified API endpoints, frontend component changes, and a checklist for the engineer
   - Guardrails: no implementation code; design only; flag risks
2. Add `architect-agent` entry to `.bob/custom_modes.yaml`
3. Append an "Architect Agent" entry to `docs/NOTES.md`

**Relevant Context**
- Current schema: `todos` table with `id, title, completed, created_at`
- API Blueprint at `/api/todos` in `todo-app/backend/routes.py`
- Frontend API client at `todo-app/frontend/src/api.js`

---

### Sub-Task 5 — Build the Engineer Mode and Skill

**Status**: `[ ] pending`

**Intent**
Create the Engineer agent role. It reads the Architecture Design section of the workflow document and implements the changes — modifying backend and frontend files, running tests, and documenting what was done. This is the only role that writes code. The same mode is reused on a second pass (after review) to address reviewer feedback — the skill detects which pass it is on by checking whether the Review Feedback section already exists in the workflow document.

**Expected Outcomes**
- `.bob/skills/engineer/SKILL.md` exists with Engineer operating instructions
- A single `engineer-agent` mode entry in `.bob/custom_modes.yaml` with full read/write tool access
- **First pass**: Engineer reads Architecture Design, implements it, fills `## Implementation Notes`
- **Second pass** (if Reviewer requests changes): Engineer reads Review Feedback, addresses it, fills `## Improvement Notes`
- The skill instructions describe how to detect the current pass automatically

**Todo List**
1. Create `.bob/skills/engineer/SKILL.md` with:
   - Role definition: software engineer implementing a technical design
   - Input: feature-workflow.md
   - Pass detection: if `## Review Feedback` section is empty or absent → first pass (implement); if it is filled → second pass (address feedback)
   - First-pass instructions: implement the Architecture Design following existing code conventions, run backend tests with pytest, fill `## Implementation Notes`
   - Second-pass instructions: read Review Feedback, address all blocking issues, fill `## Improvement Notes`
   - Code conventions to follow: Flask Blueprint pattern, SQLite with `get_db()`, React functional components with hooks, centralized `api.js` client, Tailwind CSS only (no component libraries)
   - Guardrails: do not deviate from the Architecture Design without flagging it; write tests for new backend routes following existing test patterns in `tests/test_routes.py`
2. Add a single `engineer-agent` entry to `.bob/custom_modes.yaml` with full file read/write access
3. Append an "Engineer Agent" entry to `docs/NOTES.md`

**Relevant Context**
- Backend test pattern: `todo-app/backend/tests/test_routes.py` — isolated SQLite via `tmp_path`, Flask test client
- Backend entry: `todo-app/backend/app.py`, `models.py`, `routes.py`
- Frontend entry: `todo-app/frontend/src/App.jsx`, `api.js`, `components/`
- Run tests: `cd todo-app/backend && uv run pytest`

---

### Sub-Task 6 — Build the Reviewer Mode and Skill

**Status**: `[ ] pending`

**Intent**  
Create the Reviewer agent role. It reads the implementation (code diffs or changed files) alongside the Architecture Design and PM Analysis sections, then writes structured review feedback — flagging issues, suggesting improvements, and giving an approval or change-request verdict.

**Expected Outcomes**
- `.bob/skills/reviewer/SKILL.md` exists with Reviewer operating instructions
- Reviewer mode entry in `.bob/custom_modes.yaml` with read-only tool access
- When activated, the Reviewer reads the workflow document and the changed files, then fills in the `## Review Feedback` section with categorized issues (blocking vs. suggestions) and an approval status

**Todo List**
1. Create `.bob/skills/reviewer/SKILL.md` with:
   - Role definition: senior engineer doing a code review
   - Input: feature-workflow.md (reads PM Analysis, Architecture Design, Implementation Notes)
   - Files to review: whatever the Implementation Notes section lists as changed
   - Review checklist: correctness, test coverage, security (no secrets, no 0.0.0.0 binding), API contract consistency, frontend error handling, code style consistency
   - Output format: filled-in `## Review Feedback` section with: blocking issues list, suggestions list, overall verdict (Approved / Changes Required)
   - Guardrails: read-only; do not modify code; only write to the Review Feedback section
2. Add `reviewer-agent` entry to `.bob/custom_modes.yaml` with read-only file access
3. Append a "Reviewer Agent" entry to `docs/NOTES.md`

**Relevant Context**
- Security rules from `.bob/rules/` (global rules) — reviewer must flag violations
- Existing test file conventions: `tests/test_routes.py`

---

### Sub-Task 7 — Create Feature Request Catalogue and Run End-to-End Demo

**Status**: `[ ] pending`

**Intent**
Prove the end-to-end workflow works with a real feature request. Create a catalogue of candidate feature requests (simple → complex) so watch-party participants can pick any one and run the workflow. Run the demo with **Priorities** as the baseline example, but document all options.

**Feature Request Catalogue**

| Feature | Complexity | What it touches |
|---|---|---|
| **Priorities** | Low | +1 DB column, +1 filter param, UI badge |
| **Tags / Labels** | Low-Medium | Many-to-many table, tag CRUD endpoints, UI chips |
| **Due Dates** | Low-Medium | +1 DB column, date input, overdue highlighting |
| **Search / Filter** | Medium | No schema change, query param filtering, UI search bar |
| **Kanban Board** | Medium-High | Status column, drag-and-drop UI, grouped view |
| **Analytics Dashboard** | High | Aggregation queries, chart component, read-only view |
| **Team Collaboration** | High | Users table, ownership FK, sharing permissions, auth |
| **Notifications** | High | Background job, notification table, real-time or polling UI |

Each feature request will be stored as its own markdown file in `feature-requests/` so participants can swap them in.

**Expected Outcomes**
- `feature-requests/` directory contains one markdown file per feature in the catalogue
- `feature-workflows/add-priorities-workflow.md` exists and contains all sections filled in by each agent role (the demo run)
- Code changes for the Priorities feature are present in the repo (backend schema, API, frontend UI)
- Backend tests pass after the engineer's implementation
- `docs/NOTES.md` updated with demo run observations (what worked, what needed manual correction)

**Todo List**
1. Create `feature-requests/add-priorities.md` — the demo feature (low / medium / high priority field)
2. Create `feature-requests/add-tags.md` — tags/labels feature request
3. Create `feature-requests/add-due-dates.md` — due dates feature request
4. Create `feature-requests/add-search.md` — search and filter feature request
5. Create `feature-requests/kanban-board.md` — Kanban board feature request
6. Create `feature-requests/analytics-dashboard.md` — analytics dashboard feature request
7. Run the demo: activate PM → Architect → Engineer → Reviewer → Engineer (if needed) using `add-priorities.md`
8. Verify backend tests pass: `cd todo-app/backend && uv run pytest`
9. Append a "Demo Run: Priorities Feature" section to `docs/NOTES.md` documenting observations, manual corrections needed, and lessons learned

**Relevant Context**
- Priorities: adds one column (`priority TEXT DEFAULT 'medium'`), one sort/filter param, a UI badge — minimal full-stack change
- `todo-app/backend/tests/test_routes.py` — new tests required for priority-aware creation and filtering
- `feature-workflows/` directory should be created as part of this sub-task
- More complex features (Kanban, Team Collaboration) are included in the catalogue so experienced participants can push further

---

## File Map

```
watch_party_building_ai_agents/
├── docs/
│   └── NOTES.md                          # Documentation journal (Sub-Task 1)
├── templates/
│   └── feature-workflow.md               # Handoff document template (Sub-Task 2)
├── feature-requests/
│   ├── add-priorities.md                 # Demo feature request (Sub-Task 7)
│   ├── add-tags.md                       # Catalogue entry (Sub-Task 7)
│   ├── add-due-dates.md                  # Catalogue entry (Sub-Task 7)
│   ├── add-search.md                     # Catalogue entry (Sub-Task 7)
│   ├── kanban-board.md                   # Catalogue entry (Sub-Task 7)
│   └── analytics-dashboard.md           # Catalogue entry (Sub-Task 7)
├── feature-workflows/
│   └── add-priorities-workflow.md        # Filled-in workflow for demo (Sub-Task 7)
├── .bob/
│   ├── mcp.json                          # Existing (do not modify)
│   ├── custom_modes.yaml                 # All 4 agent modes (Sub-Tasks 3-6)
│   └── skills/
│       ├── pm/SKILL.md                   # PM skill (Sub-Task 3)
│       ├── architect/SKILL.md            # Architect skill (Sub-Task 4)
│       ├── engineer/SKILL.md             # Engineer skill (Sub-Task 5)
│       └── reviewer/SKILL.md             # Reviewer skill (Sub-Task 6)
└── todo-app/
    ├── backend/                          # Modified by Engineer in Sub-Task 7
    └── frontend/                         # Modified by Engineer in Sub-Task 7
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Agent implementation | Bob mode + skill (combined) | Mode provides tool scoping and persona; skill provides detailed instructions |
| Handoff mechanism | Single living workflow markdown file | All context in one place; no inter-process communication needed |
| Feature request input | Plain markdown file | Simple, no GitHub dependency, easy to create manually |
| Code output | Direct file changes | No PR automation in v1; GitHub integration is a future step |
| Demo feature | Priorities (low/medium/high) | Simple enough to not overwhelm but exercises the full stack |
| Feature catalogue | 6 pre-written feature requests | Participants can swap in any feature; more complex options available |
| Documentation | docs/NOTES.md journal | Watch-party participants need a running record of decisions and caveats |
