# Extensions & Ideas

Once you have run the basic workflow, here are ideas to explore further.

---

## Add More Feature Requests

The `feature-requests/` folder is just markdown files — add your own and run the pipeline against them. The only requirement is a clear **Acceptance Criteria** section so the Reviewer has something concrete to check against.

---

## Add MCP Servers

MCP servers give every Bob agent access to external tools. Good candidates for this workflow:

| MCP server | Why it's useful |
|---|---|
| **GitHub MCP** (`@modelcontextprotocol/server-github`) | Issues, PRs, and code search directly in Bob |
| **Jira / Linear MCP** | Pull real tickets as feature requests instead of local files |
| **Sentry / Datadog MCP** | Let the Engineer check whether a change broke anything in production |
| **Postgres / SQLite MCP** | Let the Architect query the live DB schema before designing changes |
| **Slack MCP** | Post the final report to a channel when the pipeline finishes |

Public MCP servers are indexed in the [Bob Marketplace](https://bob.ibm.com) — browse them with `search_assets` or the Bob Marketplace MCP.

---

## Add Skills

Skills are markdown instruction files that load into any mode on demand. Ideas:

- **Security Review skill** — checks the [OWASP Top 10](https://owasp.org/www-project-top-ten/) against every changed file; blocks the Reviewer from approving if a critical finding exists.
- **Documentation skill** — generates a `CHANGELOG.md` entry and updates API docs automatically after each approved feature.
- **Test-quality skill** — checks that coverage did not drop and that every acceptance criterion has a corresponding test.

---

## Security and Vulnerability Scanning

Integrate automated security checks directly into the pipeline:

- Add a **Bob security rule** (already partially in this repo via `.bob/rules/`) that fires on every code edit.
- Have the Reviewer skill run `bandit` (Python) or `npm audit` (frontend) and include the output in its verdict.
- Add a dedicated **Security Agent** mode that runs between the Engineer and Reviewer — it scans for secrets, outdated dependencies, and known CVEs before the code review happens.

---

## CI/CD and DevOps Agent

Extend the pipeline beyond the PR:

- Add a **CI Agent** mode that watches a GitHub Actions workflow run and reports failures back into the workflow document.
- Add a **Deployment Agent** that triggers a staging deployment after the PR is merged and runs smoke tests.
- Use Bob lifecycle **hooks** (`on_stop`) to automatically push a branch and open a draft PR as soon as the Reviewer approves.

---

## Other Ideas

- **Multi-repo support** — point the Engineer Agent at a monorepo and have it touch multiple packages in one pass.
- **Feedback loop agent** — reads closed GitHub issues labelled `bug` and generates regression tests automatically.
- **Changelog agent** — runs after every merge and keeps `CHANGELOG.md` up to date using the workflow documents as input.
- **Load-testing agent** — runs `locust` or `k6` after the Engineer finishes and includes the results in the Reviewer's checklist.
- **Diagram agent** — generates an updated architecture diagram (Mermaid) whenever the DB schema or API surface changes.

---

## Bonus: "Swarm" of SDLC Agents with Git Worktrees

Run **multiple features in parallel** — one full PM → Engineer → Reviewer pipeline per worktree, each on its own branch, without interfering with each other.

### Why worktrees?

A normal `git clone` ties you to one checked-out branch at a time. `git worktree` lets you check out additional branches into separate directories, all sharing the same `.git` history. Each Bob conversation opened against a different worktree directory is completely isolated.

### How to set it up

```bash
# From the repo root — create a worktree for each feature
git worktree add ../watch-party-due-dates  -b feature/add-due-dates
git worktree add ../watch-party-search     -b feature/add-search
git worktree add ../watch-party-tags       -b feature/add-tags
```

Open each `../watch-party-<feature>/` folder as a **separate Bob workspace** (File → Open Folder). Start an **Orchestrator Agent** conversation in each workspace and send the matching feature request.

All three pipelines run concurrently, write to their own workflow documents, and commit to separate branches. When a pipeline finishes, merge its branch back into `main`.

```bash
# Clean up finished worktrees
git worktree remove ../watch-party-due-dates
# repeat for the others
```
