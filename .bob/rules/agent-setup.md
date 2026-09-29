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
