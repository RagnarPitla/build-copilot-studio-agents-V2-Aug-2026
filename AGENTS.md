# Copilot Studio Agent Kit

Instructions for any AI coding agent working in this repository.
GitHub Copilot CLI, Claude Code, Codex and Cursor all read this file.

Your job here is one of two things:

1. **Upgrade** a classic Copilot Studio agent to the modern GitHub Copilot harness, with skills.
2. **Build** a new modern agent, with skills, from a description.

Both start from a link or a description the user gives you. Work autonomously, but
never publish without asking.

---

## Non-negotiables

1. **Never publish without explicit approval.** Pushing to draft is fine and expected.
   Publishing makes the agent live for every user it is shared with. Always ask first.
2. **Never delete or overwrite the source agent.** An upgrade creates a *new* agent.
   The classic one stays untouched so the user can compare and roll back.
3. **Verify from the server, never from your own success message.** An HTTP 201 and a
   clean `pac` round trip both prove nothing. Read the component back and diff it.
   See `docs/04-gotchas.md`, this has burned people repeatedly.
4. **Do not port one for one.** Upgrading is a redesign. Turning every topic into a
   skill and every variable into memory reproduces yesterday's structure in new YAML.
5. **State what you did not verify.** If you could not test something, say so plainly
   rather than implying it works.

---

## Step 0: what am I dealing with?

The user gives you a Copilot Studio URL. Read the path segment:

| URL contains | Harness | Skills? | What to do |
|---|---|---|---|
| `/bots/<id>` | Standard, classic | No | Upgrade path |
| `/agents/<id>` | GitHub Copilot harness, modern | Yes | Build or edit in place |

The URL can be stale, so confirm against the environment. The authoritative signal is
the recognizer: `GenerativeAIRecognizer` is classic, `CLICopilotRecognizer` is modern.

```bash
python3 tools/mcs_skills.py assess --env-url <dataverse-url> --bot-id <guid>
```

The environment GUID in the URL is **not** the Dataverse URL. Resolve it:

```bash
pac env list          # match the environment GUID, take its Dataverse URL
```

`assess` prints the harness, every component broken down by kind, and a verdict.
Run it before doing anything else, and show the user the output.

---

## Step 1: prerequisites

```bash
az login                                   # Dataverse token for the tools here
pac auth create --environment <env-url>    # Power Platform CLI
pac auth list
```

`pac` must be newer than 2.9.3. Check with `pac --version`.

**If the user has the legacy `skills-for-copilot-studio` plugin installed, warn them.**
It only understands classic orchestration and Microsoft documents it as conflicting
with the current plugin. Recommend removing or disabling it.

---

## Step 2 (upgrade only): understand the classic agent before changing anything

Clone it and read it. Do not skim.

```bash
pac copilot clone --bot <guid> --environment <env-url> --output-dir ./source-agent
```

Produce a capability inventory. For each topic, tool, knowledge source and child agent,
write down **what outcome it delivers for a user**, not what components it uses. That
outcome list is what you are preserving. The components are not.

Classic components you will meet, by `kind`:

| kind | What it is |
|---|---|
| `AdaptiveDialog` | classic topic |
| `GptComponentMetadata` | the classic agent root |
| `TaskDialog` | tool or action |
| `AgentDialog` | child agent |
| `KnowledgeSourceConfiguration` | knowledge |
| `ExternalTriggerConfiguration` | trigger |

---

## Step 3: decide where each capability belongs

This is the part that matters. The modern harness has six places to put behavior, and
the rule is: **every behavior belongs in the smallest component that makes it reliable
and inspectable.**

| Component | Holds |
|---|---|
| **Instructions** | what is always true, global behavior |
| **Knowledge** | searchable facts, things the agent must ground in or cite |
| **Tools** | system actions and integrations |
| **Memory** | context that must persist |
| **Skills** | situational, reusable, multi-step procedures |
| **Connected agents** | genuine specialist domains |

Deciding between them:

- Always applies to every conversation? **Instructions**, not a skill.
- Agent needs to *search* it (RAG)? **Knowledge**.
- Agent needs to *follow* it step by step? **Skill**, plus a tool to fetch the file.
- A single function call? **Tool**, not a skill.
- A procedure with inputs, steps, confirmations and outputs? **Skill**.
- Exact maths or file generation? **Skill with a bundled Python script**, so the
  sandbox runs deterministic code instead of the model predicting a result.
- A real specialist domain with its own remit? **Connected agent**.

Classic topics almost never map cleanly onto skills. A deterministic dialog flow
usually becomes instructions plus a tool, and sometimes a skill.

**Show the user this mapping and get agreement before you author anything.**

---

## Step 4: create the target agent

An upgrade produces a new agent. Create it in the target environment, then author into it.

```bash
pac copilot init --authoring-mode cli-copilot --display-name "<Name> V2"
```

Name it distinctly. Two similarly named agents in one environment is a genuine hazard
on a customer call, so make the V2 obvious.

---

## Step 5: author

Instructions go in `settings.mcs.yml` under `configuration.agentSettings`. There is no
`agent.mcs.yml` on the modern harness, and creating one is a mistake.

Skills are `SKILL.md` files. Format, front matter and limits are in
`docs/03-skills-format.md`. Read it before writing your first skill, because the
storage format is not what you would guess and is not publicly documented.

Write skills that state: when to invoke, required inputs, what to ask when inputs are
missing, the steps, confirmation rules for anything with side effects, expected output,
and what to do on failure. Prefer several focused skills over one large one.

Before deploying:

```bash
python3 tools/mcs_skills.py validate --path ./my-skills
```

---

## Step 6: deploy to draft

```bash
pac copilot push --project-dir ./target-agent          # instructions, tools, knowledge
python3 tools/mcs_skills.py add --env-url <env> --bot-id <guid> --path ./my-skills
```

**`pac copilot push` does not create skills.** It reports success and silently creates
nothing for new ones. This is the single most expensive trap in this repo. Skills go
through `mcs_skills.py`, which writes them the way the product actually stores them.

---

## Step 7: verify, then hand back

```bash
python3 tools/mcs_skills.py list   --env-url <env> --bot-id <guid>
python3 tools/mcs_skills.py export --env-url <env> --bot-id <guid> --out /tmp/verify
diff -r ./my-skills /tmp/verify
```

Then report honestly:

- capabilities preserved, and where each one landed
- anything that did **not** survive, and why
- what you tested, and what you did not
- the exact publish command, for the user to run themselves

Treat your own output as a first draft. Ask the user to compare the new agent's
behavior against the old one on the journeys that actually matter.

---

## Tooling in this repo

| Command | Purpose |
|---|---|
| `assess` | harness, components by kind, verdict |
| `agents` | list agents in an environment to find a GUID |
| `list` | skills on an agent |
| `add` | create or update skills from `SKILL.md`, idempotent |
| `export` | pull deployed skills back to `SKILL.md` |
| `remove` | delete a skill |
| `validate` | check `SKILL.md` offline, touches nothing |
| `package` | one shareable zip per skill |

Run with `python3 tools/mcs_skills.py <command> --help`.

---

## Related official work

Microsoft's CAT team ships an experimental plugin that automates much of the upgrade,
`/mcs-assistant:migrate`. When it fits the user's setup, recommend it, it is good, and
this repo is not trying to replace it. See `docs/05-sources.md`.

This repo exists to be harness-agnostic, to carry the verified skill storage format, and
to provide the verification step that any generated upgrade still needs.
