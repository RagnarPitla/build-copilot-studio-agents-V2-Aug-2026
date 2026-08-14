# Gotchas

Every one of these was hit for real. They are in rough order of how much time they cost.

---

## 1. componenttype 13 looks like the skill type. It is not.

The option set lists `13 = Skill (V2)`, which is the obvious choice. Modern skills are
`componenttype 9` with `kind: InlineAgentSkill`.

Components written at type 13 are created successfully, return HTTP 201, and round trip
perfectly through `pac copilot clone`. They simply never appear as skills.

**Symptom:** you deployed skills, the API said yes, and the portal shows none.
**Check:** read the components back and look at `kind`, not `componenttype`.

---

## 2. `pac copilot push` does not create skills.

Push round-trips components that already exist. Give it a workspace containing new skill
files and it reports `Push complete` having created nothing at all.

Use `tools/mcs_skills.py add` for skills. Push remains correct for instructions, tools
and knowledge.

**Symptom:** a successful push, and no new skills.

---

## 3. A clean `pac` round trip proves nothing.

`pac` echoes the `data` column verbatim. Writing `kind: TotallyMadeUpKind` round trips
byte for byte and looks like a pass.

Round-tripping proves the bytes survived. It says nothing about whether the product
understands them. The only real check is that the component appears and behaves as a
skill.

---

## 4. Counting componenttype 9 tells you nothing about shape.

Type 9 holds skills, child agents, MCP tools, actions and classic topics. A classic
agent and a modern agent can both be dominated by type 9 rows.

Identify the harness from the recognizer instead:

| Recognizer | Harness |
|---|---|
| `GenerativeAIRecognizer` | classic, Standard |
| `CLICopilotRecognizer` | modern, GitHub Copilot |

`tools/mcs_skills.py assess` does this and breaks components down by `kind`.

---

## 5. The bundled language server reports false errors on skills.

Validating a workspace containing skills can report, per skill file:

```
Missing required property 'AppId'
Missing required property 'AppEndpoint'
```

That is the schema for the legacy bot-to-bot skill feature, a different thing that
shares the name. **Do not add those properties and do not delete the files.**

Everything outside the skills folder should validate cleanly. Failures there are real.

---

## 6. The legacy plugin conflicts with the current one.

`copilot-studio@skills-for-copilot-studio` only understands classic orchestration.
Microsoft's own migration flow checks for it and recommends removing or disabling it
before using `mcs-assistant@copilot-studio-plugin`.

If both are installed, expect confusing behavior.

---

## 7. `pac copilot init` creates a classic agent unless told otherwise.

Without `--authoring-mode cli-copilot` you get a Standard-harness agent. If you then
author a modern agent into it, everything validates, pushes, and is the wrong shape.

**Always clone the real target rather than initialising a lookalike.** The mistake is
invisible until you open the portal.

---

## 8. There is no `agent.mcs.yml` on the modern harness.

The widely repeated rule "confirm the workspace has `agent.mcs.yml` before authoring" is
true only for classic agents. On the modern harness that file does not exist and
creating one is itself the error. The marker is `settings.mcs.yml` carrying
`configuration.agentSettings`.

---

## 9. `settings.mcs.yml` is not schema-validated.

Invented properties inside it produce zero diagnostics. A clean validation run does not
mean instructions landed where you intended. Prove it by pushing, reading back, and
diffing.

---

## 10. Push after an out-of-band write fails with a conflict.

Writing components through the API and then pushing gives
`Remote changes conflict with local changes`.

Rather than fighting `pull`, clone fresh into a temp directory, copy your changed files
over it, and push from there.

---

## 11. schemaname is capped at 100 characters.

It is derived from the bot schema name plus the skill name. Long skill names overflow it
and the failure is not obvious. `validate` warns when a name is at risk.

---

## 12. The environment GUID in the URL is not the Dataverse URL.

A Copilot Studio URL carries an environment GUID. The tools need the Dataverse URL,
for example `https://yourorg.crm.dynamics.com`. Map between them with `pac env list`.
