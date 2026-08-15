# Sources

Everything this repository is based on, with what each one is good for. All were read
while building the kit.

---

## Official product documentation

The authoritative source. Where this repo and a blog post disagree, this wins.

| Link | Covers |
|---|---|
| [Choose a harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | **Start here.** All three harnesses compared, and the statement that agents cannot be transferred between them |
| [Agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview) | The GitHub Copilot harness, its components, the agent lifecycle, and the Build / Preview / Evaluate / Monitor tabs |
| [Build an agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/build-overview) | The Build tab in detail: instructions editor plus the components panel |
| [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview) | What skills are, and the official `SKILL.md` plus ZIP package format |
| [Create a skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-create) | Authoring in the portal, and the naming rule this repo validates against |
| [Add an existing skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing) | Uploading a `.md` or a `.zip`. The supported no-code deployment path |
| [Usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) | Copilot Credits. Billing starts when you start building, not at publish |
| [Tools overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-overview) | Actions and integrations |
| [Memory](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/memory-overview) | Persistent context across conversations |
| [Select a model](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-select-agent-model) | Model choice, a component this repo previously omitted |
| [Power Platform CLI](https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction) | `pac`, required newer than 2.9.3 |
| [About GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) | The CLI harness this repo runs under |

---

## Microsoft CAT team blog

The most useful current material on the modern harness.

**[New orchestrator resources](https://microsoft.github.io/mcscatblog/posts/new-orchestrator-resources/)**
The best single starting point. Introduces four resources: the deep dive deck, the
technical mini-site, the migration plugin, and the skills gallery. Source of the
component-model rule this repo follows: every behavior belongs in the smallest component
that makes it reliable and inspectable, with instructions carrying what is always true,
knowledge the searchable facts, tools the system actions, memory the persistent context,
skills the situational procedures, and connected agents the specialist domains.
Also the warning worth repeating: do not turn every topic into a skill and every
variable into memory just because they existed.

**[Migration plugin video demo](https://microsoft.github.io/mcscatblog/posts/migration-plugin-video-demo/)**
A full upgrade run end to end with GitHub Copilot CLI. Shows a classic child agent
becoming a skill, and makes the case for capability-led rather than one-for-one
conversion. Explicitly frames the output as a strong first draft to be reviewed.

**[Copilot Studio agent sandbox](https://microsoft.github.io/mcscatblog/posts/copilot-studio-agent-sandbox/)**
Why agents get a Python sandbox: models predict plausible results rather than computing
correct ones. Covers the trade-off between code the model writes at runtime and a script
packaged inside a skill, and why knowledge retrieval lands files in the sandbox.

**[Redlining documents](https://microsoft.github.io/mcscatblog/posts/redlining-documents-new-copilot-studio-experience/)**
A worked example of a skill carrying a script to produce a real `.docx` with genuine
tracked changes.

**[Modern agents have skills now](https://microsoft.github.io/mcscatblog/posts/modern-mcs-agent-skills/)**
Skills as task-specific instructions plus scripts, delivered when needed.

**[Skills for Copilot Studio](https://microsoft.github.io/mcscatblog/posts/skills-for-copilot-studio/)**
Background on how the terminal-based approach started.

**[Claude Code plugin demo](https://microsoft.github.io/mcscatblog/posts/claude-copilot-skills-copilot-studio-plugin-demo/)**
Authoring an agent with the plugin, the step before migration.

---

## Tooling and samples

**[microsoft/copilot-studio-plugin](https://github.com/microsoft/copilot-studio-plugin)**
The official experimental plugin, successor to `skills-for-copilot-studio`. Provides
`/mcs-assistant:migrate` and four sub-agents: architect, describer, init and manage.
Requires `pac` newer than 2.9.3.

```
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
/mcs-assistant:migrate Upgrade this agent to the GitHub Copilot harness: <url> from tenant <id>
```

Microsoft describes it as an experimental research project, not an officially supported
product, and advises reviewing generated YAML before pushing. **If it fits your setup,
use it.** This repo is not trying to replace it.

**[skills-for-copilot-studio](https://github.com/microsoft/skills-for-copilot-studio)**
The predecessor. Classic orchestration only, and documented as conflicting with the
current plugin. Remove or disable it.

**[CAT Agent Skills gallery](https://microsoft.github.io/cat-agent-skills/)**
A community collection of reusable skills, each a drop-in `SKILL.md`, some with script
bundles. Filter to Copilot Studio. Often faster than writing a skill from scratch, and
a good reference for how a well-formed skill reads.

**[Technical Deep Dive deck](https://aka.ms/CopilotStudioDeepDiveDeck)**
Decision framework for what to build where, and an honest read on what is not yet
supported.

**[Technical guide mini-site](https://aka.ms/MCSTechGuide)**
The BlastBox Omega sample, deployable into your own environment, with two scenarios
showing where each responsibility belongs.

---

## Verified independently for this repo

The **authoring** format is documented by Microsoft, and what this repo produces was
checked against those pages and matches: `SKILL.md`, YAML front matter carrying `name`
and `description`, Markdown instructions, and an optional ZIP with supporting files.

The **storage** format in `03-skills-format.md` is not documented anywhere. It was
derived by inspecting real skill components in a live environment and confirmed by
deploying, reading back and diffing. Where this repo states a storage detail, it was
checked against a live tenant rather than inferred. See `04-gotchas.md` for what that
process caught, including the component type that accepts skills and silently never
renders them.
