# Copilot Studio: GitHub Copilot Harness

Read [AGENTS.md](../AGENTS.md) before doing anything in this repository. It is the
source of truth for the method, the component model, and the rules.

Custom agents live in `.github/agents/`:

- **mcs-upgrade** - convert a classic Copilot Studio agent to the modern harness with skills
- **mcs-build** - build a new modern agent with skills

Never publish an agent without explicit approval, never modify the source agent during
an upgrade, and always verify changes by reading them back from the server.
