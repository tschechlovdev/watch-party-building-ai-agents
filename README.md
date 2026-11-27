# The Agentic Development Team with IBM Bob

An AI development team inside [IBM Bob](https://bob.ibm.com): a **PM**, an **Architect**,
an **Engineer** and a **Reviewer**, driven by an **Orchestrator**. Each role is a Bob
mode with a skill file. They don't talk to each other directly: they hand over through
**one markdown document per feature or bug**. No agent framework, no message queue, no
vector database.

The same team works in two places:

- **In the IDE:** you give the orchestrator a feature request, the team designs,
  implements, tests and reviews it in a full-stack todo app (Flask + React).
- **As a software factory light:** a GitHub issue with the label `bug` starts the team
  in GitHub Actions. Bob triages the bug, fixes it, the workflow runs the tests, and a
  pull request comes back. A person reviews and merges.

## The workshops

| Session | What you do | Guide |
|---|---|---|
| **Part 1: Building an Agentic SDLC Workflow with Bob** | Build the team: modes, skills, the markdown handoff, the orchestrator | [`docs/WORKSHOP-1.md`](docs/WORKSHOP-1.md), lab guide [`docs/INSTRUCTIONS.md`](docs/INSTRUCTIONS.md) |
| **Part 2: A Software Factory Light with Bob for Automated Bugfixing** | Find a bug between features, let the orchestrator file it, let the Bug Factory fix it in GitHub Actions | [`docs/WORKSHOP-2.md`](docs/WORKSHOP-2.md) |

> 🧑‍💻 **Joining a session?** Create your own copy with **Use this template** (leave
> *Include all branches* unticked), not by cloning or forking this repo. Then follow
> the guide of your session.

## Quick start

```bash
gh repo create my-agent-team --public --clone \
  --template tschechlovdev/watch-party-building-ai-agents
cd my-agent-team
cd todo-app/backend && uv run pytest -q && cd ../..     # 94 passed
```

Open the folder in Bob, start a new conversation in **SDLC Orchestrator Agent** mode, and
try:

```text
When I tick a todo as done in the list view, it still shows up in "To Do" on the board.
```

Needs: Bob, Python 3.11+ with `uv`, Node.js 18+, Git, and the GitHub CLI `gh`.
For the Bug Factory also a Bob API key ([`docs/WORKSHOP-2.md`, Part 3](docs/WORKSHOP-2.md#part-3--turn-on-the-factory-then-let-the-orchestrator-file-the-issue)). Set it up **before** you file the bug issue.

## What is on `main`, and how to go back

`main` is where Part 2 starts: the todo app with a Kanban board, due dates, priorities
and search, all built by the agent team, **and one bug** between those features. Earlier
states are on checkpoint branches:

| State | Branch |
|---|---|
| End of Part 1: plain todo app + agent team | `checkpoint/0-start` |
| + Kanban board | `checkpoint/1-kanban` |
| + due dates, priorities, search, the bug | `main` |

How to copy a checkpoint into your own repo: [`docs/WORKSHOP-2.md`, Go back in time](docs/WORKSHOP-2.md#go-back-in-time-optional).

## How it works

### Features: the SDLC pipeline

```text
Feature request (.md file or GitHub issue)
    ↓
Orchestrator: bug or feature? → feature branch + feature-workflows/<slug>-workflow.md
    ↓
PM: user stories, acceptance criteria
    ↓
Architect (optional): schema, API, components
    ↓
Engineer: code, tests, pytest
    ↓
Reviewer (read-only): Approved → PR  |  Changes Required → Engineer again (max 2 cycles)
```

### Bugs: the Bug Factory in GitHub Actions

```text
Issue with label `bug` (often a vague one-liner)
    ↓
bob-bug-triage.yml → bug-triage-agent
    ↓  comment: symptom, file:line evidence, root cause, fix options, regression test
Gate: small and clear AND reporter is a collaborator?
    ├─ yes → the fix starts automatically
    └─ no  → a maintainer adds the label `bob-fix`
    ↓
bob-bug-fix.yml → engineer-agent → reviewer-agent (max 2 cycles)
    ↓  CI gate: pytest + lint + build (Bob's own test run is not trusted)
Pull request "fix: … (#n)" with Fixes #n. A person merges.
```

Each Bob call is one headless Bob Shell run in one mode; **the workflow is the
orchestrator**. The bug workflow document `bug-workflows/issue-<n>-workflow.md` is the
shared memory, like the feature workflow document.

**Safety rails**
- Issue text is untrusted. It reaches Bob only through a file, quoted and marked as
  data, never through `${{ }}` in a script.
- The Bob steps get no GitHub token. Only the workflow comments, pushes and opens PRs,
  after its own checks.
- Bob can only change files in `todo-app/` and `bug-workflows/`.
- Off by default: the workflows run only with your API key and `BOB_ENABLED=true`
  (set by `scripts/setup-bug-factory.sh`). PRs are never merged automatically.

## Repository structure

```text
.
├── .bob/
│   ├── custom_modes.yaml        # Orchestrator, PM, Architect, Engineer, Reviewer, Bug Triage
│   ├── skills/                  # one SKILL.md per role
│   └── rules/                   # rules for all modes
├── .github/
│   ├── workflows/bob-bug-*.yml  # Bug Factory: triage and fix
│   ├── actions/bob-run/         # runs one Bob mode headless and checks its marker
│   └── scripts/bug_workflow.py  # builds the bug document, comments and PR body
├── docs/
│   ├── WORKSHOP-1.md            # Part 1 guide
│   ├── INSTRUCTIONS.md          # Part 1 lab guide (step by step)
│   ├── WORKSHOP-2.md            # Part 2 guide
│   ├── SESSION-RUNBOOK.md       # Part 2 presenter script
│   └── BUG-FACTORY-DEMO.md      # Bug Factory demo script
├── feature-requests/            # feature ideas; two are not built yet (tags, analytics)
├── feature-workflows/           # one handoff document per built feature
├── bug-workflows/               # one handoff document per bug fixed by the factory
├── templates/                   # blank feature and bugfix workflow documents
├── scripts/                     # setup-bug-factory.sh, create-feature-issues.sh
├── todo-app/                    # Flask + SQLite backend, React + Vite frontend
├── sdlc_agents_spec.md          # specification of the four agents
└── orchestrator_agent_spec.md   # specification of the orchestrator
```

## Further resources

* Agent specification: [`sdlc_agents_spec.md`](sdlc_agents_spec.md)
* Orchestrator specification: [`orchestrator_agent_spec.md`](orchestrator_agent_spec.md)
* Ideas for going further: [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md)

## License

[MIT](LICENSE). Free to use, copy and adapt for workshops and teaching.
