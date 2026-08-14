# Skills format

How a skill is actually stored, verified against real skills in a live environment.
This is not publicly documented at the storage level, and it is not what you would
guess, so it is written down here in full.

---

## The authoring format: `SKILL.md`

One folder per skill, containing a `SKILL.md`:

```markdown
---
name: validate-product
description: >-
  Validate every line item from a parsed purchase order against released products
  in Dynamics 365 F&O. All lines must pass before an order is created.
---

# Validate product

## When to invoke
After validate-customer returns status = "matched".

## Inputs
| Field | Type | Notes |
|---|---|---|
| lines | array | Full line array from parse output |

## Workflow
### Step 1 - item number lookup
...
```

Front matter takes `name` and `description`. Everything below is Markdown instructions.

**`description` is the routing text.** The orchestrator decides whether to invoke the
skill by reading it, so it must describe when the skill applies, not just what it is.
A vague description means the skill never fires. Write it for a dispatcher, and include
the situations, phrases and conditions that should trigger it.

Rules for `name`: lowercase letters, digits and single hyphens. It also becomes part of
the Dataverse `schemaname`, which is capped at 100 characters, so keep it short.

---

## The storage format

A skill is a `botcomponent` row:

| Column | Value |
|---|---|
| `componenttype` | **9** |
| `data` | `kind: InlineAgentSkill` plus a `content:` block holding the whole `SKILL.md` |
| `description` | the routing text |
| `name` | the skill name |
| `schemaname` | `<botschemaname>.skill.<skill-name>_<3 chars>`, max 100 |
| `parentbotid` | the bot |

The `data` column looks like this:

```yaml
kind: InlineAgentSkill
content: |
  ---
  name: validate-product
  description: |-
    Validate every line item from a parsed purchase order...
  ---
  <!-- bic:source=blank -->

  ## When to Invoke
  ...
```

Two things to notice:

- **`content` carries the entire `SKILL.md`, front matter included**, indented two
  spaces. The front matter is not stripped out into columns; it is duplicated.
- The body is nested inside `data`. There is a separate `content` *column* on the
  table, and it is not used for this. The `content` here is a YAML key inside `data`.

---

## componenttype 9 is not "skill"

This is the part that costs people time. Type 9 is a container for many component
kinds, discriminated by the `kind` field inside `data`:

| kind | What it is |
|---|---|
| `InlineAgentSkill` | a skill |
| `AgentDialog` | a child agent |
| `McpTool` | an MCP tool |
| `TaskDialog` | a tool or action |
| `WorkflowTool` | a workflow tool |
| `AdaptiveDialog` | a classic topic |

**Counting componenttype 9 tells you nothing.** Always read `kind`. A modern agent with
six child agents and six skills has twelve type-9 components.

There is also a `componenttype 13` labelled "Skill (V2)" in the option set. It is not
what the modern harness uses. Writing skills there produces components that exist, round
trip cleanly through `pac`, and never appear as skills in the product. That mistake is
the reason this document exists.

---

## How this was verified

The format was not taken from documentation, because none covers the storage layer.

1. An initial attempt used `componenttype 13` with `kind: Skill`. The components were
   created successfully and `pac copilot clone` round-tripped them byte for byte.
   **They still did not appear as skills in the portal.**
2. A search across a whole environment for components whose `data` contained
   `InlineAgentSkill` returned real, working skills belonging to other agents. Every one
   was `componenttype 9`.
3. Reading one of those rows in full gave the exact shape above, which matches the
   format the official Microsoft plugin authors.
4. The six wrong components were rewritten in this format and the originals deleted.
   Re-reading from the server confirmed six `InlineAgentSkill` components at type 9 and
   zero at type 13.

The lesson worth keeping: a clean `pac` round trip proves the bytes survived, not that
the format is correct. `pac` echoes `data` verbatim, including formats the product does
not understand.

---

## Size

The object model contains the string "Instructions should be 8000 characters or fewer."
In practice skills larger than that have been created and round-tripped without
complaint, and shipped child agents already exceed it, so the limit appears to bind a
different property. Keep it in mind if a skill ever refuses to save with no useful
error, but do not design around it. Splitting an oversized skill into focused ones is
better practice anyway.

---

## Skills, or something else?

Skills are for **situational, reusable, multi-step procedures**. The most common
authoring mistake is putting the wrong thing in a skill:

| If it is | Put it in |
|---|---|
| Always true for every conversation | Instructions |
| Something to search or cite | Knowledge |
| A single system call | A tool |
| A procedure with steps, inputs and confirmations | A skill |
| Exact arithmetic or file generation | A skill with a Python script |
| A whole specialist domain | A connected agent |

A skill can carry supporting files, including Python scripts. The agent sandbox runs
them, which is the right way to get exact totals or a genuinely valid `.docx`, rather
than asking a model to predict the output.
