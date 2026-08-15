# Skills that interview you

These two are for the coding agent, not for Copilot Studio. They make the agent ask you
the right questions before it builds anything, which is the single biggest difference
between an agent that demos well and one that survives contact with real users.

| Skill | What it does |
|---|---|
| [grill-my-agent](grill-my-agent/SKILL.md) | Interviews you before an agent is built or upgraded, one question at a time, until every behavior is assigned to exactly one component and you have approved the design |
| [grill-my-skills](grill-my-skills/SKILL.md) | Takes the quality warnings from `validate` and turns each one into a real question, then rewrites the skills |

They are already wired in. `mcs-build` and `mcs-upgrade` are told to run `grill-my-agent`
before authoring and `grill-my-skills` before deploying, so you do not need to invoke
them by hand. Ask for them by name if you want them on their own.

## Install them anywhere

They follow the same convention as [mattpocock/skills](https://github.com/mattpocock/skills),
so they work outside this repo too:

```bash
npx skills@latest add RagnarPitla/build-copilot-studio-agents-V2-Aug-2026 --skill grill-my-agent
```

## Why they are shaped like this

Borrowed from `grill-me`, and worth keeping if you write your own:

- **One question at a time.** A wall of twelve questions gets one vague answer.
- **Always recommend an answer.** You should usually be able to reply "yes" and move on.
- **Never ask what is discoverable.** For an existing agent that means running `assess`
  and `pac copilot clone` and reading everything first, so the agent tells you what your
  agent does rather than asking you.

## They are the repo's own thesis

These are `SKILL.md` files with the same front matter as everything in `examples/`,
so `tools/mcs_skills.py` treats them as first-class:

```bash
python3 tools/mcs_skills.py validate --path skills --strict
```

Both pass clean, and they did not at first. The checker flagged them, the warnings were
fair, and they were rewritten. That is the loop this repo is asking you to run, so it
runs on itself.
