---
name: skill-name-here
description: >-
  One or two sentences that tell the orchestrator WHEN to use this skill, not just what
  it is. Name the situations, user phrasings and conditions that should trigger it. This
  text is how the agent decides to invoke the skill, so a vague description means it
  never fires. Replace this entirely.
---

# Skill name here

One line on what this skill accomplishes.

## When to invoke

- The specific situation that should trigger this skill
- Another triggering condition
- When NOT to use it, if there is a neighbouring skill it could be confused with

## Inputs

| Field | Type | Required | Notes |
|---|---|---|---|
| `example_id` | string | yes | Where it comes from |
| `options` | object | no | Defaults if absent |

If a required input is missing, ask for it. Do not guess, and do not proceed with a
placeholder.

## Steps

### Step 1 - short title

What to do, and how to tell whether it worked.

### Step 2 - short title

Include the decision rules explicitly. Say what happens when the answer is ambiguous.

## Confirmation rules

Anything with a side effect must be confirmed before it happens. State exactly what to
show the user and what counts as approval. Delete this section only if the skill is
strictly read-only.

## Output

What the user gets back, and in what shape. Be specific: a table, a file, a short
summary, a decision plus reasons.

## When it fails

- Input was not found: what to say and what to offer
- The tool errored: whether to retry, and how many times
- Out of scope: which skill or person to hand off to

Never invent a result when a step fails. Say what failed and what you need.

---

Notes on writing skills, delete before shipping:

- `name` must be lowercase letters, digits and single hyphens. Keep it short; it becomes
  part of a Dataverse schemaname capped at 100 characters.
- Prefer several focused skills over one large one.
- Do not restate global behavior that belongs in instructions.
- If a step needs exact arithmetic or must produce a real file, put a Python script
  beside this file and tell the skill to run it. The agent sandbox executes it, which is
  reliable in a way that asking a model to compute is not.
- Validate before deploying: `python3 tools/mcs_skills.py validate --path ./skills`
