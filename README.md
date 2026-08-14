# Copilot Studio Agent Kit

Clone this repo, point your AI coding agent at it, and either **upgrade a classic
Copilot Studio agent** to the modern GitHub Copilot harness with skills, or **build a
new one** from a description.

Works with GitHub Copilot CLI, Claude Code, and any harness that reads `AGENTS.md`.

```
"Upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>"
```

That is the whole interface. The agent resolves the environment, assesses the harness,
clones the classic agent, proposes where each capability belongs, builds a V2 with
skills, deploys to draft, and verifies the result from the server.

It never publishes, and it never touches your original agent.

---

## Quick start

```bash
git clone https://github.com/RagnarPitla/copilot-studio-agent-kit.git
cd copilot-studio-agent-kit

pip install -r tools/requirements.txt
az login
pac auth create --environment https://YOURORG.crm.dynamics.com
```

`pac` must be newer than 2.9.3 (`pac --version`).

Then start your agent in this folder and ask for what you want.

**GitHub Copilot CLI**

```bash
copilot
> upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
```

**Claude Code**

```bash
claude
> /upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
> /build an agent that triages bank statement import failures
```

**Anything else** reads `AGENTS.md` and follows it.

---

## What you get

| | |
|---|---|
| `AGENTS.md` | The method. Every harness reads this |
| `.github/agents/` | `mcs-upgrade`, `mcs-build` for GitHub Copilot CLI |
| `.claude/agents/`, `.claude/commands/` | The same, plus `/upgrade` and `/build` |
| `tools/mcs_skills.py` | Assess agents, and deploy and verify skills |
| `docs/` | Harness differences, upgrade playbook, skills format, gotchas, sources |
| `templates/` | A starter `SKILL.md` |
| `examples/` | Six real skills from a deployed D365 agent |

---

## Check any agent in one command

```bash
python3 tools/mcs_skills.py assess \
  --env-url https://YOURORG.crm.dynamics.com --bot-id <guid>
```

```
agent      SalesOrderAgent
recognizer GenerativeAIRecognizer
shape      1  (classic, Standard harness)

components (26), by kind
  AdaptiveDialog                  13   classic topic
  TaskDialog                       7   tool / action
  AgentDialog                      1   child agent
  KnowledgeSourceConfiguration     1   knowledge

verdict
  Classic agent on the Standard harness. Skills are not available here.
```

Other commands: `agents`, `list`, `add`, `export`, `remove`, `validate`, `package`.

---

## Why this exists

Upgrading is a redesign, not a format conversion. The classic model is topics and
dialogs; the modern one spreads behavior across instructions, knowledge, tools, memory,
skills and connected agents. Porting one for one gives you a modern agent shaped like a
classic one.

There are also traps that cost real time, all documented in `docs/04-gotchas.md`:

- **`pac copilot push` does not create skills.** It reports success and creates nothing.
- **The obvious component type for a skill is the wrong one.** Skills written there are
  accepted, round trip perfectly through `pac`, and never appear in the product.
- **A clean `pac` round trip proves nothing.** `pac` echoes stored data verbatim,
  including formats the product does not understand.
- **The language server reports false errors** on every valid skill file.

The skill storage format is not publicly documented. The one in `docs/03-skills-format.md`
was verified against real skills in a live tenant, then confirmed by deploying, reading
back and diffing.

---

## Relationship to Microsoft's plugin

Microsoft's CAT team ships an experimental plugin that automates much of the upgrade:

```
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
```

**If it fits your setup, use it.** This repo does not replace it. It is harness-agnostic,
it carries the verified storage format, and it adds the verification step that any
generated upgrade still needs, since Microsoft is explicit that the output is a first
draft to be reviewed.

Note that the older `skills-for-copilot-studio` plugin conflicts with the current one.
Remove or disable it.

Full reading list in `docs/05-sources.md`.

---

## Safety

- Deploys to **draft only**. Publishing is always left to you.
- **Never modifies the source agent** during an upgrade.
- Verifies by reading back from the server rather than trusting a success message.

---

## License

MIT
