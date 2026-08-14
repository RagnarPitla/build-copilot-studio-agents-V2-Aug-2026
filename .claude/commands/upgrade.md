---
description: Upgrade a classic Copilot Studio agent to the modern harness with skills.
argument-hint: A Copilot Studio agent URL
---

Upgrade the Copilot Studio agent at $ARGUMENTS to the modern GitHub Copilot harness,
creating a new V2 agent with skills.

Follow `.claude/agents/mcs-upgrade.md` and `AGENTS.md` exactly.

Do not modify or delete the source agent, and do not publish. Stop and show the user
the proposed architecture before authoring anything, and verify from the server with
`export` plus a `diff` before reporting.
