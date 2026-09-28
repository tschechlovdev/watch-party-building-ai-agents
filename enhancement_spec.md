# Agentic SDLC Team with Bob

## Goal

Build a minimal but extensible Agentic SDLC workflow around an existing Todo application.

The workflow should demonstrate how Bob can support the software development lifecycle from idea to implementation and review.

The solution should be designed so that additional capabilities can easily be added later.

---

# Core Workflow

```text
Code Base
    ↓
Feature Request
    ↓
Agent Team
    ↓
Implementation
    ↓
Review
    ↓
Improvement
    ↓
Pull Request
    ↓
Merge
```

A possible implementation could look like:

```text
GitHub Issue
    ↓
PM
    ↓
Architect
    ↓
Engineer
    ↓
Reviewer
    ↓
Engineer
    ↓
PR
    ↓
Merge
```

However, the exact responsibilities, interactions and agent architecture should be decided during implementation.

---

# Application

Use the existing Todo application as the foundation.

The AI should propose several possible feature requests that vary in complexity.

Examples:

- Kanban Board
- Team Collaboration
- Priorities
- Tags
- Attachments
- Notifications
- Analytics Dashboard

The implementation should support experimenting with different feature requests.

---

# Design Principles

- Focus on working end-to-end workflows.
- Prefer simplicity over sophistication.
- Keep components loosely coupled.
- Design for extensibility.
- Make it easy to add additional agents later.
- Make it easy to replace individual agents.
- Avoid framework-specific assumptions where possible.

---

# Evolution Path

The initial version should focus on a working workflow.

Potential future extensions may include:

- Skills
- Subagents
- Feedback loops
- Hooks
- MCP integrations
- GitHub automation
- Security reviews
- Testing agents
- UI generation
- Enterprise deployment

These should be treated as optional extensions rather than initial requirements.

---

# Expected Outcome

At minimum, the system should be able to:

```text
Feature Request
    ↓
Collaborative Agent Workflow
    ↓
Code Changes
    ↓
Review Feedback
    ↓
Improved Implementation
```

Everything else should be considered an enhancement.

---

# Guiding Principle

Optimize for working end-to-end workflow first,
extensibility second,
sophistication third.