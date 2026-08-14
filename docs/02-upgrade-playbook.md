# Upgrade playbook

Classic Standard-harness agent, to a modern agent with skills.

The hard part is not the mechanics. It is deciding what the modern agent should be.
Mechanical conversion produces a modern agent shaped like a classic one, which throws
away most of the benefit.

---

## Before you start

- `pac` newer than 2.9.3. Check with `pac --version`.
- `az login`, for the Dataverse token the tools here use.
- Remove or disable the legacy `skills-for-copilot-studio` plugin if present.
- Know where the upgraded agent is going. Same environment is fine; the new agent is
  separate from the old one either way.

**The source agent is never modified.** An upgrade creates a new agent, so the classic
one remains for comparison and rollback.

---

## Step 1: assess

```bash
pac env list      # environment GUID from the URL -> Dataverse URL
python3 tools/mcs_skills.py assess --env-url <dataverse-url> --bot-id <bot-guid>
```

If the recognizer already says `CLICopilotRecognizer`, there is nothing to upgrade.

---

## Step 2: inventory capabilities, not components

```bash
pac copilot clone --bot <guid> --environment <env-url> --output-dir ./source-agent
```

Read all of it. For each topic, tool, knowledge source and child agent, write down the
**outcome it delivers for a user**.

The outcome list is what you carry forward. The component list is not.

A worked example. A classic sales order agent with 13 topics and 7 actions might reduce
to five real outcomes:

| Outcome | Classic implementation |
|---|---|
| Parse an incoming purchase order | 3 topics plus a document action |
| Confirm the customer exists | 2 topics plus a lookup action |
| Validate every line against released products | 4 topics plus 2 actions |
| Create the sales order | 2 topics plus an action |
| Explain why an order was rejected | 2 topics |

Thirteen topics, five outcomes. That gap is the whole point of upgrading.

---

## Step 3: map each outcome to a component

Use the model in `AGENTS.md`. Every behavior belongs in the smallest component that
makes it reliable and inspectable.

Continuing the example:

| Outcome | Modern home | Why |
|---|---|---|
| Parse a purchase order | Skill with a Python script | Deterministic extraction, exact output |
| Confirm the customer | Skill plus existing lookup tool | A procedure with a decision, not one call |
| Validate lines | Skill | Multi-step, with clear pass and fail rules |
| Create the order | Tool, with confirmation in instructions | A single system write |
| Explain a rejection | Instructions | Always true, applies to every conversation |

Things that will not carry across, and must be called out rather than quietly dropped:

- **Power Fx** does not exist. Re-express the intent as a skill, a tool, an instruction,
  or a script inside a skill.
- **Topic-level turn control.** The modern orchestrator decides what to do next. If a
  flow depended on exact turn sequencing, restate it as rules inside a skill.
- **Unsupported actions.** AI Prompts and some connector actions do not convert. List
  them as gaps.
- **Variables.** Do not mechanically turn them into memory. Most were plumbing.

**Show the user this table and get agreement before authoring anything.**

---

## Step 4: create the target

```bash
pac copilot init --authoring-mode cli-copilot --display-name "SalesOrderAgent V2"
```

Without `--authoring-mode cli-copilot` you get another classic agent.

Name it so nobody can confuse it with the original. Two similar names in one environment
is a real hazard during a demo.

---

## Step 5: author

Instructions go in `settings.mcs.yml` under `configuration.agentSettings`. They carry
what is always true: the agent's remit, tone, what it must confirm before acting, and
what it must never do.

Skills are `SKILL.md` files, one folder each. Start from
`templates/skill-template/SKILL.md`, read `docs/03-skills-format.md`, and look at
`examples/` for six real deployed skills.

Prefer several focused skills to one large one. Do not create skills that duplicate
instructions or knowledge retrieval.

```bash
python3 tools/mcs_skills.py validate --path ./skills
```

---

## Step 6: deploy to draft

```bash
pac copilot push --project-dir ./target-agent
python3 tools/mcs_skills.py add --env-url <env> --bot-id <new-guid> --path ./skills
```

`pac copilot push` does not create skills. It will report success and create none.

---

## Step 7: verify

```bash
python3 tools/mcs_skills.py export --env-url <env> --bot-id <new-guid> --out /tmp/verify
diff -r ./skills /tmp/verify
```

A clean diff is the evidence the deployment landed. Also open the agent in the portal
and confirm the skills are listed, because a component can exist without being a skill.

---

## Step 8: test against the old agent

The upgrade is a first draft until proven otherwise.

- Run the journeys that actually matter through both agents.
- Try the inputs that used to break the classic one.
- Confirm every write action still asks for confirmation.
- Check that failure paths produce something useful.

Only then publish, and let the user do it.

---

## Using the official plugin instead

Microsoft's CAT team ships an experimental plugin that automates most of steps 2 to 5:

```
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
/mcs-assistant:migrate Upgrade this agent to the GitHub Copilot harness: <url> from tenant <id>
```

It analyses the classic agent, proposes an architecture and generates the upgraded
agent. It is good, and where it fits, use it.

Steps 1, 7 and 8 still apply. Microsoft is explicit that the output is a first draft to
be reviewed, and the verification in this repo is what turns that draft into something
you can put in front of a customer.
