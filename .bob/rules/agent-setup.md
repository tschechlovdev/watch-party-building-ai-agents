# Agentic SDLC — Setup Reminder

This workspace uses five custom Bob modes and five skills for an agentic SDLC workflow.
The agent modes are: **Orchestrator Agent**, **PM Agent**, **Architect Agent**, **Engineer Agent**, **Reviewer Agent**.

## If `use_skill` returns "Skill not found"

This means Bob has not yet indexed the workspace skills. Fix:
1. Close this conversation.
2. Open a **new** Bob conversation in this workspace.
3. Switch to the desired agent mode and try again.

Skills are scanned once at Bob startup. A fresh conversation always sees them.

## Skill names (for `use_skill`)

| Mode | Skill name |
|---|---|
| Orchestrator Agent | `orchestrator` |
| PM Agent | `pm` |
| Architect Agent | `architect` |
| Engineer Agent | `engineer` |
| Reviewer Agent | `reviewer` |

## Never use `disable-model-invocation: true` in these skills

The SDLC agent skills must NOT have `metadata: disable-model-invocation: true` in their
frontmatter — that flag prevents Bob from indexing them in the `use_skill` lookup table.
The skills already have narrow enough descriptions to avoid accidental auto-triggering.

## Bug Hunter skills

There is one mode for all bug work: **Bug Hunter Orchestrator Agent**
(`bug-hunter-orchestrator-agent`). It picks the skill from your request:

| Say | Skill | What happens |
|---|---|---|
| "find bugs" | `bug-finder` | Checks the app against the checklist and files one GitHub issue per failing check (label `bug-hunter`). Changes no code. |
| "fix bugs" | `bug-fixer` | Fixes the open `bug-hunter` issues with proof, pushes branch `bug-fixes` and opens a PR. Never merges. |
| "find and fix everything" | `bug-hunter` | Find and fix in one run, no GitHub. |

It delegates to `engineer-agent` and `bug-hunter-reviewer-agent` only, as subtasks that
close themselves with `end_subtask`. Start it as a new top-level chat on a clean tree.
`bug-finder` and `bug-fixer` reuse the checklist and message templates of `bug-hunter`.
