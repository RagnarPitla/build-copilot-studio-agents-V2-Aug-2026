---
name: grill-my-skills
description: Interrogate and rewrite Copilot Studio skills until each one is specific enough to actually fire and safe enough to run, using the offline quality checker plus targeted questions about routing, inputs, confirmations and failure handling. Use when skills are written but weak, when a skill never triggers or triggers on the wrong thing, or when the user asks to review, harden or improve their skills.
---

Grill me about my skills until each one is specific enough to fire on the right request
and safe enough to run on the wrong one. One skill at a time, one question at a time,
always with your recommended answer.

## When to invoke

Use this when skills already exist and need to be better: one never fires, two fight over
the same request, or the checker is noisy. For designing an agent that does not exist
yet, use `grill-my-agent` first.

## Inputs

You require a folder containing one or more `SKILL.md` files. If I have not told you
where they are, look in `skills/`, `examples/`, or the agent workspace you cloned, and
tell me which you found rather than asking me to repeat myself.

## Start with the checker, not with me

```bash
python3 tools/mcs_skills.py validate --path <folder-of-skills>
```

That reports errors and quality warnings for every skill. Work its output rather than
your own impressions. Fix every error before you ask me anything, because errors block
deployment and there is nothing to discuss.

Then take the warnings one skill at a time. Do not read me the warning list. Turn each
warning into a real question.

## What each warning is really asking

**Routing description is short, or never says when to use this.** This is the single
highest-leverage thing in the file. The orchestrator picks skills by matching the request
against this description and nothing else, so a vague one either never fires or fires
constantly. Ask me: what would a user actually type when they need this? Use my words,
not the internal jargon. Then write a description that names the trigger, the domain and
the outcome, and read it back to me.

**No "when to invoke" section.** Ask me for the boundary case: name me a request that
looks like this skill but should go somewhere else. That negative example is worth more
than three positive ones, and it is what stops two skills fighting over the same request.

**No inputs section.** Ask me what the agent must have in hand before it can start, and
crucially what it should do when something is missing. Guess, or ask? Almost always ask,
and the skill has to say so explicitly or the model will invent a plausible value.

**No ordered steps.** A skill that reads as prose gets skimmed. Ask me to walk you
through what a competent human does, in order, and write that down as numbered steps.

**No failure handling.** Ask me what actually goes wrong in practice: the system is down,
the record is locked, the numbers do not agree, the user asked for something out of
scope. For each, what should it say and what must it not do? An agent with no failure
path will improvise one, and it will improvise confidently.

**Has side effects but never asks for confirmation.** Stop and get this explicitly.
Which of these actions can it take on its own, and which need me to say yes first? Write
the confirmation into the steps at the exact point it happens, not as a general warning
at the top, because a warning at the top gets rationalised away.

**Body is very short.** Ask the honest question: does this need to be a skill at all?
A couple of lines of always-true guidance belongs in the agent's instructions. A skill
earns its place by being a procedure.

## Also grill these, which no checker can see

- Two skills whose descriptions overlap. Read them side by side and ask me which one
  should win. If neither obviously wins, they are one skill.
- A skill that overlaps a connected agent. Same question, and it matters more, because
  the orchestrator will pick one and you will not easily see which.
- Any arithmetic in prose. If the skill tells the model to compute a total, that is a
  number the model will predict rather than calculate. Ask whether this should carry a
  Python script instead.
- Claims about the platform. If the skill asserts what the product can or cannot do,
  ask me how we know. Unverified claims sound authoritative and get repeated to customers.

## Finish

1. Rewrite the skills. Show me a before and after of the routing description for each
   one, since that is the change most likely to alter behavior.
2. Re-run the checker and show me it is clean:

```bash
python3 tools/mcs_skills.py validate --path <folder-of-skills> --strict
```

3. Tell me plainly that a clean checker means the skills are well formed, not that they
   are correct. Only running them against my real examples shows that.
