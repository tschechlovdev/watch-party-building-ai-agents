#!/usr/bin/env bash
# Turn the feature requests in feature-requests/*.md into GitHub issues in YOUR
# copy of this repository, so the orchestrator can start from an issue URL.
#
# Usage (from the repository root):
#   ./scripts/create-feature-issues.sh             # create the issues
#   ./scripts/create-feature-issues.sh --dry-run   # only show what would be created
#
# Safe to run twice: a feature that already has an issue with the same title is skipped.
# Features that are already built (their feature-workflows/<name>-workflow.md says
# current-role: done) are skipped too.
# If gh cannot find your repo (for example with an SSH host alias), set it explicitly:
#   GH_REPO=<your-login>/my-agent-team ./scripts/create-feature-issues.sh

set -euo pipefail

UPSTREAM="tschechlovdev/watch-party-building-ai-agents"
DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
skip() { printf '  \033[33m-\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; exit 1; }

[ -d feature-requests ] || fail "run this from the repository root"

if ! $DRY_RUN; then
  command -v gh >/dev/null 2>&1 || fail "gh is not installed. See https://cli.github.com"
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null) \
    || fail "gh cannot find your repo. Run: GH_REPO=<your-login>/<repo> $0"
  [ "$REPO" = "$UPSTREAM" ] && fail "this is the workshop repo itself. Run it in your own copy."
  echo "Creating feature issues in $REPO"
  gh label create feature --color 0E8A16 --description "New capability" --force >/dev/null
  EXISTING=$(gh issue list --state all --label feature --limit 200 --json title -q '.[].title')
else
  EXISTING=""
  echo "Dry run: nothing is created"
fi

for f in feature-requests/*.md; do
  # "# Feature Request: Kanban Board" -> "Kanban Board"
  title=$(head -n 1 "$f" | sed -E 's/^#[[:space:]]*(Feature Request:[[:space:]]*)?//')
  [ -n "$title" ] || title=$(basename "$f" .md)
  wf="feature-workflows/$(basename "$f" .md)-workflow.md"
  if [ -f "$wf" ] && grep -Eq '^current-role:[[:space:]]*done' "$wf"; then
    skip "$title (already built)"
    continue
  fi
  if printf '%s\n' "$EXISTING" | grep -Fxq "$title"; then
    skip "$title (issue exists)"
  elif $DRY_RUN; then
    ok "$title  <- $f"
  else
    url=$(gh issue create --title "$title" --body-file "$f" --label feature)
    ok "$title  $url"
  fi
done
