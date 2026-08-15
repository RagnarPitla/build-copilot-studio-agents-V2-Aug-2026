# Build Copilot Studio Agents with the GitHub Copilot Harness

Read [AGENTS.md](AGENTS.md). It is the single source of truth for how to work in this
repository and applies to Claude Code exactly as written.

Two agents are available in `.claude/agents/`:

- **mcs-upgrade** - convert a classic Copilot Studio agent to the modern harness with skills
- **mcs-build** - build a new modern agent with skills from a description

And two slash commands in `.claude/commands/`:

- `/upgrade <copilot-studio-url>`
- `/build <description>`

Non-negotiables, repeated here because they matter most: never publish without asking,
never modify the source agent during an upgrade, and always verify from the server
rather than trusting a success message.
