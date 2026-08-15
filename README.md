# Copilot Studio: GitHub Copilot Harness

**Move your Copilot Studio agents onto the GitHub Copilot harness, with skills, from
just a URL.**

Clone this repo, point your AI coding agent at it, and hand it a Copilot Studio link.
It upgrades a standard harness agent onto the GitHub Copilot harness, or builds a new
agent there from a description.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Harness](https://img.shields.io/badge/runs%20in-Copilot%20CLI%20%7C%20Claude%20Code%20%7C%20any-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-working%2C%20early-orange)

```
> upgrade https://copilotstudio.microsoft.com/environments/<env>/bots/<id>
```

That is the whole interface.

The agent resolves the environment, detects which harness you are on, clones the source
agent, works out where each capability belongs in the new component model, builds a V2
with skills, deploys it to draft, and then verifies the result by reading it back from
the server.

It never publishes, and it never touches your original agent.

---

## Why it creates a new agent instead of converting yours

Because Microsoft says you cannot convert one:

> Agents created with the GitHub Copilot harness can't be transferred to the standard
> harness, and vice versa.
>
> [Choose a harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

So an upgrade is a rebuild, and the interesting question is not "where does this topic
go" but "what outcome does this deliver, and what is now the smallest component that
delivers it". Port one for one and you get a modern agent shaped like a standard one.

---

## The three harnesses

A harness is the runtime between your agent and the model. It decides when to call the
model, what to send, how to read the answer, and which tools to call. Copilot Studio has
three, and only one of them has skills.

| | GitHub Copilot harness | Standard harness | Copilot chat harness |
|---|---|---|---|
| **Best for** | Complex, multi-step business processes | Rule-based agents, structured conversations | Extending M365 Copilot Chat |
| **How it works** | Reasons through a goal step by step | Follows the topics and rules you define | Grounds M365 Copilot Chat in your content |
| **Recovers from failure** | Retries, finds another path | Follows the paths you built | Not a focus |
| **Files** | Creates and edits Word, Excel, PowerPoint, PDF | Not a focus | Not a focus |
| **Skills and memory** | **Yes** | No | No |
| **Billing** | Copilot Credits, usage-based | Licensing | Consumption or M365 Copilot USLs |

This repo moves agents from the **standard harness** to the **GitHub Copilot harness**.
Copilot chat is a different target and is out of scope.

---

## Know this before you upgrade: billing changes

Not a footnote. On the GitHub Copilot harness:

- Usage is billed in **Copilot Credits**, usage-based.
- Credits cover LLM tokens, tools, knowledge, MCP, and the harness itself.
- **Billing starts when you start building**, not when you publish. Building, previewing,
  testing and generating evaluations all consume credits.

That is a real change from the standard harness, which bills after publish. Check your
credit position before a large migration. Consumption shows on the agent's **Monitor**
tab. See [usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview).

---

## Quick start

```bash
git clone https://github.com/RagnarPitla/copilot-studio-github-copilot-harness.git
cd copilot-studio-github-copilot-harness

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

Nothing writes until you ask. Point `assess` at any agent and see what you have:

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

## Where behavior goes

The GitHub Copilot harness spreads behavior across components configured on the **Build**
tab. The rule that keeps an agent maintainable: **every behavior belongs in the smallest
component that makes it reliable and inspectable.**

| Component | Holds | Reach for it when |
|---|---|---|
| **Instructions** | Identity, tone, scope, what is always true | It applies to every conversation |
| **Knowledge** | Searchable, citable sources | The agent needs to *search* it |
| **Tools** | Connectors, MCP servers, REST APIs, workflows | It is a single system call |
| **Skills** | Reusable structured procedures | The agent needs to *follow* it, step by step |
| **Memory** | Context that survives the conversation | It must persist |
| **Connected agents** | Specialist domains | It has its own genuine remit |
| **Model** | Which model reasons | Always. Choose it deliberately |

A standard-harness topic rarely becomes a skill. Most become instructions plus a tool.

> Don't turn every topic into a Skill and every variable into memory. That's archaeology
> with YAML.

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
| `examples/` | Six real skills from a deployed D365 finance agent, with templates and reference files |

The examples are not toys. They are the skills from a working bank reconciliation agent,
including the CSV templates and reference material they load at runtime.

---

## On skills, and what is actually undocumented

Microsoft documents the **authoring** format, and this repo matches it exactly: a
`SKILL.md` with YAML front matter carrying `name` and `description`, Markdown
instructions, and an optional ZIP with supporting files such as scripts and templates.
That was checked against
[Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)
and confirmed, including the naming rule this repo validates against.

**So use the supported path when it fits.** For one or two skills, package and upload:

```bash
python3 tools/mcs_skills.py package --path ./my-skills --out ./dist
```

Then in the portal: **Build** tab, **Skills**, **Add skill**, **Upload a skill**. It
takes a `.md` or a `.zip`.

What is *not* documented anywhere is the **storage** format, how a skill actually lands
in Dataverse. You need it only when deploying programmatically rather than clicking
upload, which is what an automated upgrade does. That is in
[`docs/03-skills-format.md`](docs/03-skills-format.md), derived from real skills in a
live tenant and confirmed by deploying, reading back and diffing.

---

## The traps

All twelve are in [`docs/04-gotchas.md`](docs/04-gotchas.md). The expensive ones:

- **There is a component type that looks exactly right for a skill and is not.** Write a
  skill there and the API accepts it, `pac` round trips it, every tool reports success,
  and the skill never appears in the product. Silently invisible.
- **`pac copilot push` does not create skills.** It reports success and creates nothing.
- **A clean `pac` round trip proves nothing.** `pac` echoes stored data back verbatim,
  including formats the product cannot render. `kind: TotallyMadeUpKind` round trips fine.
- **The language server reports false schema errors** on every valid skill file.
- **`pac copilot init` gives you a standard harness agent** unless you pass
  `--authoring-mode cli-copilot`.
- **The environment GUID in the portal URL is not the Dataverse URL.**
- **The legacy `skills-for-copilot-studio` plugin conflicts** with the current one.

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
| `package` | One uploadable zip per skill, supporting files included | No |
| `add` | Create or update skills, idempotent | Draft |
| `remove` | Delete a skill | Draft |

Nothing publishes. Ever. That stays your call.

---

## Safety rails

- **Draft only.** The tools deploy to draft. Publishing makes an agent live for everyone
  it is shared with, so it is left to you, with the exact command handed back.
- **Your original agent is never touched.** An upgrade creates a new agent, so you can
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

**If it fits your setup, use it.** This repo is not trying to replace it and recommends
it where it fits. What this adds: it is harness-agnostic, it carries the verified storage
format, and it supplies the verification step that any generated upgrade still needs,
since Microsoft is explicit that the output is a first draft for review.

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
| [`docs/05-sources.md`](docs/05-sources.md) | You want the official material, annotated |

---

## Status and contributing

Early but working. The tooling has been exercised end to end against live agents: full
create, update, read back, diff and delete, plus lossless export round trips and refusal
cases. What has had less mileage is the sheer variety of standard-harness agents in the
wild, so if an upgrade produces something odd, that is the interesting bug.

Issues and pull requests welcome, especially:

- agents whose harness or shape the assessment gets wrong
- skills that deploy but do not behave as expected
- anything in `docs/04-gotchas.md` that turns out to be fixed

---

## Credits

Built on Microsoft Learn documentation for the GitHub Copilot harness, and on the public
guidance from Microsoft's Copilot Studio CAT team, in particular their orchestrator
resources, agent sandbox and migration plugin posts. Full annotated reading list in
[`docs/05-sources.md`](docs/05-sources.md).

## License

MIT. See [LICENSE](LICENSE).
