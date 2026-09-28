# feature-workflows/

This directory holds filled-in workflow documents — one per feature request that has been run
through the Agentic SDLC workflow end-to-end.

## How to create a new workflow run

1. Copy `templates/feature-workflow.md` to this directory:
   ```
   cp templates/feature-workflow.md feature-workflows/<feature-name>-workflow.md
   ```
2. Edit the front matter: set `feature`, `requester`, and leave `current-role: pm`.
3. Switch to PM mode (`pm-agent`) and point it at the workflow document and the feature request.

## Demo run

The demo feature is `add-priorities` — see `feature-requests/add-priorities.md`.
Run it by following the Workflow Overview in `docs/NOTES.md`.
