#!/usr/bin/env bash
# Set up the Bob Bug Factory in YOUR copy of this repository.
#
# Usage (from the repository root):
#   ./scripts/setup-bug-factory.sh              # configure the current repo
#   ./scripts/setup-bug-factory.sh --demo-issue # ... and open the demo bug issue
#
# What it does:
#   1. checks that gh is installed and logged in
#   2. enables Issues and Actions on the repo
#   3. stores your Bob API key as the Actions secret BOB_API_KEY
#      (from $BOB_API_KEY if set, otherwise gh asks for it with hidden input)
#   4. allows GitHub Actions to create pull requests
#   5. creates the labels the workflows use
#   6. optionally opens the demo bug issue
#
# Your API key is sent only to GitHub's encrypted secret store of YOUR repo.

set -euo pipefail

UPSTREAM="tschechlovdev/watch-party-building-ai-agents"
DEMO_ISSUE=false
[ "${1:-}" = "--demo-issue" ] && DEMO_ISSUE=true

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; exit 1; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

step "1. GitHub CLI"
command -v gh >/dev/null 2>&1 || fail "gh is not installed. See https://cli.github.com"
LOGIN=$(gh api user -q .login 2>/dev/null) \
  || fail "gh is not logged in to github.com. Run: gh auth login --hostname github.com --web"
ok "logged in as $LOGIN"

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null) \
  || fail "run this inside your clone of the repository"
[ "$REPO" = "$UPSTREAM" ] && fail "this is the workshop repo itself. Create your own copy first (see docs/INSTRUCTIONS.md)."
PERM=$(gh api "repos/$REPO" -q .permissions.admin)
[ "$PERM" = "true" ] || fail "you need admin rights on $REPO (is the active gh account '$LOGIN' the owner? Try: gh auth switch)"
ok "repository $REPO"

step "2. Issues and Actions"
gh repo edit "$REPO" --enable-issues >/dev/null
gh api -X PUT "repos/$REPO/actions/permissions" -F enabled=true -f allowed_actions=all >/dev/null
ok "issues and actions enabled"

step "3. Bob API key (secret BOB_API_KEY)"
if [ -n "${BOB_API_KEY:-}" ]; then
  printf %s "$BOB_API_KEY" | gh secret set BOB_API_KEY -R "$REPO"
  ok "stored from \$BOB_API_KEY"
else
  echo "  Paste your Bob API key (input is hidden):"
  gh secret set BOB_API_KEY -R "$REPO"
  ok "stored"
fi
if [ -n "${BOB_TEAM_ID:-}" ]; then
  printf %s "$BOB_TEAM_ID" | gh secret set BOB_TEAM_ID -R "$REPO"
  ok "stored BOB_TEAM_ID (only needed for keys of type 'general')"
fi

step "4. Allow GitHub Actions to create pull requests"
echo '{"default_workflow_permissions":"read","can_approve_pull_request_reviews":true}' \
  | gh api -X PUT "repos/$REPO/actions/permissions/workflow" --input - >/dev/null
ok "enabled"

step "5. Labels"
label() { gh label create "$1" --color "$2" --description "$3" --force -R "$REPO" >/dev/null; ok "$1"; }
label bug                   d73a4a "Something isn't working (starts Bob triage)"
label bob-fix               0e8a16 "Let Bob fix this bug and open a PR"
label bob-triaged           c5def5 "Bob has triaged this issue"
label bob-autofix-candidate bfdadc "Bob thinks this is a small, clear fix"
label needs-info            fbca04 "Bob needs more information from the reporter"
label bob-fix-failed        d93f0b "Bob could not deliver a verified fix"

if $DEMO_ISSUE; then
  step "6. Demo bug issue"
  URL=$(gh issue create -R "$REPO" --label bug \
    --title "Done todos become undone when I edit them" \
    --body "I had a todo marked as done and fixed a typo in it. After saving it was suddenly not done anymore?? Happened twice now. Kinda annoying")
  ok "$URL"
  echo
  echo "  Watch Bob work: gh run watch -R $REPO   (or the Actions tab)"
fi

step "Done."
echo "  Open an issue with the 'bug' label and Bob starts triaging."
echo "  Stop all Bob runs at any time: gh variable set BOB_ENABLED --body false -R $REPO"
