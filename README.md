# Copilot Studio Glow Up

**Give your Copilot Studio agents a glow up.**

Clone this repo, point your AI coding agent at it, and hand it a Copilot Studio URL.
It upgrades a classic agent to the modern GitHub Copilot harness with skills, or builds
a new one from a description.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Harness](https://img.shields.io/badge/harness-Copilot%20CLI%20%7C%20Claude%20Code%20%7C%20any-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-working%2C%20early-orange)

```
> upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
```

That is the whole interface.

The agent resolves the environment, detects which harness you are on, clones the classic
agent, works out where each capability belongs in the new model, builds a V2 with skills,
deploys it to draft, and then verifies the result by reading it back from the server.

It never publishes, and it never touches your original agent.

---

## What a glow up actually changes

Upgrading is a redesign, not a file conversion. The two harnesses think differently.

| | Standard harness (classic) | GitHub Copilot harness (modern) |
|---|---|---|
| Core unit | Topics and dialogs | Instructions, knowledge, tools, memory, skills, connected agents |
| Behavior lives in | Trigger phrases and node graphs | The smallest component that makes it reliable and inspectable |
| Reuse | Copy the topic | Share the skill |
| Exact maths, file output | Model predicts it | Skill ships a Python script the sandbox runs |
| Editing | Portal canvas | Markdown and YAML in your editor, in git |

Which is why porting one for one is the wrong move. You end up with a modern agent shaped
like a classic one. This repo asks a different question for every capability: **what
outcome does this deliver for a user**, and what is now the smallest component that
delivers it.

---

## Quick start

```bash
git clone https://github.com/RagnarPitla/copilot-studio-glow-up.git
cd copilot-studio-glow-up

pip install -r tools/requirements.txt   # PyYAML, that is all
az login
pac auth create --environment https://YOURORG.crm.dynamics.com
```

`pac` must be newer than 2.9.3. Check with `pac --version`.

Then start your agent in this folder and ask for what you want.

**GitHub Copilot CLI**

```bash
copilot
> upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
> build an agent that triages bank statement import failures
```

**Claude Code**

```bash
claude
> /upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
> /build an agent that triages bank statement import failures
```

**Anything else** reads `AGENTS.md` and follows it. Codex and Cursor work today.

---

## Try it read-only first

Nothing here writes until you ask it to. Point `assess` at any agent and see what you have:

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

No GUID handy? `python3 tools/mcs_skills.py agents --env-url <url>` lists them.

---

## What you get

| Path | What it is |
|---|---|
| `AGENTS.md` | The method. Every harness reads this. Start here if you read one file |
| `.github/agents/` | `mcs-upgrade` and `mcs-build` for GitHub Copilot CLI |
| `.claude/agents/`, `.claude/commands/` | The same two, plus `/upgrade` and `/build` |
| `tools/mcs_skills.py` | Assess agents, deploy skills, verify them. PyYAML is the only dependency |
| `docs/` | Harness differences, upgrade playbook, skill format, gotchas, sources |
| `templates/skill-template/` | A starter `SKILL.md` with the front matter filled in |
| `examples/` | Six real skills from a deployed D365 finance agent, with their templates and reference files |

The examples are not toys. They are the skills from a working bank reconciliation agent,
including the CSV templates and reference material they load at runtime.

---

## Where behavior goes

The rule from Microsoft's orchestrator guidance, and the spine of this repo: **every
behavior belongs in the smallest component that makes it reliable and inspectable.**

| Component | Holds | Reach for it when |
|---|---|---|
| **Instructions** | What is always true | It applies to every conversation |
| **Knowledge** | Searchable, citable facts | The agent needs to *search* it |
| **Tools** | System actions | It is a single function call |
| **Memory** | Context that must persist | It has to survive the turn |
| **Skills** | Situational reusable procedures | The agent needs to *follow* it, step by step |
| **Connected agents** | Specialist domains | It has its own genuine remit |

A classic topic rarely becomes a skill. Most become instructions plus a tool.

> Don't turn every topic into a Skill and every variable into memory. That's archaeology
> with YAML.

---

## Why this repo exists

Three reasons, in order of how much time they save you.

**1. The skill storage format is not publicly documented, and the obvious guess is wrong.**

There is a component type that looks exactly like the right one for a skill. Write a skill
there and the API accepts it, `pac` round trips it perfectly, every tool reports success,
and the skill never appears in the product. It is invisible. `docs/03-skills-format.md`
has the format that actually works, derived from real skills in a live tenant and then
confirmed by deploying, reading back and diffing.

**2. The traps are expensive and silent.** All twelve are in `docs/04-gotchas.md`:

- `pac copilot push` does not create skills. It reports success and creates nothing.
- A clean `pac` round trip proves nothing. `pac` echoes stored data back verbatim,
  including formats the product cannot render. `kind: TotallyMadeUpKind` round trips fine.
- The language server reports false schema errors on every valid skill file.
- `pac copilot init` gives you a classic agent unless you pass `--authoring-mode cli-copilot`.
- The environment GUID in the portal URL is not the Dataverse URL.
- The legacy `skills-for-copilot-studio` plugin conflicts with the current one.

**3. Generated upgrades need verifying, and most tooling stops at "done".** Everything
here checks its own work by reading back from the server, because a success message is
not evidence.

---

## Command reference

```bash
python3 tools/mcs_skills.py <command> --help
```

| Command | Purpose | Writes? |
|---|---|---|
| `assess` | Harness, components by kind, verdict | No |
| `agents` | List agents in an environment to find a GUID | No |
| `list` | Skills on an agent | No |
| `validate` | Check `SKILL.md` files offline | No |
| `export` | Pull deployed skills back to `SKILL.md` | No |
| `package` | One shareable zip per skill, supporting files included | No |
| `add` | Create or update skills, idempotent | Draft |
| `remove` | Delete a skill | Draft |

Nothing publishes. Ever. That stays your call.

---

## Safety rails

- **Draft only.** The tools deploy to draft. Publishing makes an agent live for everyone
  it is shared with, so it is always left to you, with the exact command handed back.
- **Your original agent is never touched.** An upgrade creates a new agent so you can
  compare the two and roll back by doing nothing.
- **Verification is from the server.** Read back and diff, never trust a 201.
- **Honest reporting.** The agents are told to state plainly what they could not verify
  rather than implying it works.

---

## Relationship to Microsoft's plugin

Microsoft's Copilot Studio CAT team ships an experimental plugin that automates much of
the upgrade:

```
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
```

**If it fits your setup, use it.** This repo is not trying to replace it and recommends it
where it fits. What this adds: it is harness-agnostic, it carries the verified skill
storage format, and it supplies the verification step that any generated upgrade still
needs, since Microsoft is explicit that the output is a first draft for review.

One warning worth repeating: the older `skills-for-copilot-studio` plugin conflicts with
the current one. Remove or disable it first.

---

## Documentation

| Doc | Read it when |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Always. It is the method |
| [`docs/01-which-harness.md`](docs/01-which-harness.md) | You are not sure what you are looking at |
| [`docs/02-upgrade-playbook.md`](docs/02-upgrade-playbook.md) | You are doing an upgrade by hand |
| [`docs/03-skills-format.md`](docs/03-skills-format.md) | Before you write your first skill |
| [`docs/04-gotchas.md`](docs/04-gotchas.md) | Something succeeded but nothing happened |
| [`docs/05-sources.md`](docs/05-sources.md) | You want the official material |

---

## Status and contributing

Early but working. The tooling has been exercised end to end against live agents: full
create, update, read back, diff and delete, plus lossless export round trips and refusal
cases. What has had less mileage is the breadth of classic agents in the wild, so if an
upgrade produces something odd, that is the interesting bug.

Issues and pull requests welcome, especially:

- classic agents whose shape the assessment gets wrong
- skills that deploy but do not behave as expected
- anything in `docs/04-gotchas.md` that turns out to be fixed

---

## Credits

Built on the public guidance from Microsoft's Copilot Studio CAT team, in particular their
orchestrator resources, agent sandbox and migration plugin posts. Full reading list with
notes on what each one is good for in [`docs/05-sources.md`](docs/05-sources.md).

## License

MIT. See [LICENSE](LICENSE).
