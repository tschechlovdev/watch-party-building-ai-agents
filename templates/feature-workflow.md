---
feature: ""
requester: ""
status: "in-progress"
current-role: "pm"
---

# Feature Workflow

<!-- INSTRUCTIONS FOR ALL AGENTS
This document is the shared memory for one feature request moving through the Agentic SDLC workflow.
Each agent role reads the sections above their own, then appends their section below.
Do not modify sections written by a previous agent.
Update the `current-role` front matter field to reflect the next role when you finish your section.
Hint comments (like this one) are guidance only — they are not part of your output.
-->

---

## Feature Request

<!-- PM AGENT: Copy the content of the feature request file here verbatim, then begin your analysis below. -->

_(paste feature request here)_

---

## PM Analysis

<!-- PM AGENT: Fill in this section.
- Write 3–5 user stories in the format: "As a [user], I want to [action] so that [benefit]."
- List 3–6 acceptance criteria as checkboxes.
- List anything explicitly out of scope.
- Do NOT propose any technical approach — focus on what the user needs, not how to build it.
- When done, set current-role to "architect" in the front matter.
-->

### User Stories

_(PM agent fills this in)_

### Acceptance Criteria

_(PM agent fills this in)_

### Out of Scope

_(PM agent fills this in)_

---

## Architecture Design

<!-- ARCHITECT AGENT: Fill in this section.
- Read the PM Analysis above and the existing codebase (models.py, routes.py, api.js, App.jsx).
- Design the minimal changes needed to satisfy the acceptance criteria.
- Write design-only content — no implementation code, no code snippets.
- Flag any risks or open questions for the engineer.
- When done, set current-role to "engineer" in the front matter.
-->

### DB Schema Changes

_(Architect agent fills this in)_

### API Changes

_(Architect agent fills this in — new endpoints or modifications to existing ones)_

### Frontend Changes

_(Architect agent fills this in — which components to add or modify)_

### Engineer Checklist

<!-- ARCHITECT AGENT: List the specific steps the engineer should follow, in order. -->

_(Architect agent fills this in)_

### Open Questions / Risks

_(Architect agent fills this in)_

---

## Implementation Notes

<!-- ENGINEER AGENT (first pass): Fill in this section after implementing the Architecture Design.
- List every file you changed and why.
- Briefly describe the approach taken.
- List the tests you added.
- Run `uv run pytest` from todo-app/backend/ and confirm tests pass before writing this section.
- When done, set current-role to "reviewer" in the front matter.

PASS DETECTION: If the Review Feedback section below is still empty, this is your first pass.
If Review Feedback is already filled in, skip this section and go to Improvement Notes instead.
-->

### Files Changed

_(Engineer agent fills this in)_

### Approach

_(Engineer agent fills this in)_

### Tests Added

_(Engineer agent fills this in)_

---

## Review Feedback

<!-- REVIEWER AGENT: Fill in this section.
- Read the PM Analysis, Architecture Design, and Implementation Notes sections above.
- Read every file listed under "Files Changed".
- Categorize issues as Blocking (must fix) or Suggestions (optional improvement).
- Check: correctness, test coverage, security (no hardcoded secrets, no 0.0.0.0 binding),
  API contract consistency with the Architecture Design, frontend error handling, code style.
- Give a final verdict: Approved or Changes Required.
- If Changes Required: set current-role to "engineer" in the front matter.
- If Approved: set current-role to "done" in the front matter.
-->

### Blocking Issues

_(Reviewer agent fills this in — or writes "None" if clean)_

### Suggestions

_(Reviewer agent fills this in — or writes "None")_

### Verdict

_(Approved / Changes Required)_

---

## Improvement Notes

<!-- ENGINEER AGENT (second pass): Fill in this section only if the Reviewer set verdict to "Changes Required".
- Address every blocking issue listed in Review Feedback.
- Note which suggestions you acted on and which you deferred (with reason).
- Re-run tests and confirm they pass.
- When done, set current-role to "reviewer" for a second review, or "done" if the reviewer approved inline.
-->

_(Engineer agent fills this in on second pass — leave blank on first pass)_

---

## Final Status

<!-- ALL AGENTS: This section is filled in last, once the reviewer approves.
- Summarise what was built.
- Note the PR reference once GitHub integration is available.
-->

**Outcome**: _(summary of what was implemented)_

**PR**: _TBD — GitHub PR creation is a future step. See docs/NOTES.md > Future Requirements._
