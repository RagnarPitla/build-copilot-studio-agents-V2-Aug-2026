# Which harness am I on?

Answer this before touching anything.

Copilot Studio has **three** harnesses. A harness is the runtime between your agent and
the model: it decides when to call the model, what to send it, how to read the response,
and which tools to call.

| Harness | Powers | Skills? |
|---|---|---|
| **GitHub Copilot harness** | Reasoning-heavy, multi-step work | **Yes** |
| **Standard harness** | Rule-based agents, agent flows, topics | No |
| **Copilot chat harness** | Extending Microsoft 365 Copilot Chat | No |

This repo is about moving from the standard harness to the GitHub Copilot harness. The
Copilot chat harness is a different target and is out of scope here.

Microsoft is explicit that this is not a conversion:

> Agents created with the GitHub Copilot harness can't be transferred to the standard
> harness, and vice versa.

That is why an upgrade here always creates a **new** agent, and why porting one for one
is the wrong instinct. See
[Choose a harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

---

## Billing changes when you cross harnesses

Worth knowing before you recommend an upgrade, because it surprises people:

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| Unit | Licensing, see Copilot Studio licensing | **Copilot Credits**, usage-based |
| Billing starts | After you publish | **The moment you start building** |
| What consumes it | Published usage | LLM tokens, tools, knowledge, MCP, and the harness itself |

Building, previewing, testing and generating evaluations all consume credits on the
GitHub Copilot harness. Credit consumption is visible on the agent's **Monitor** tab.
See [usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview).

---

## The five second check: read the URL

| URL path | Harness | Skills? |
|---|---|---|
| `/environments/<env>/bots/<id>` | **Standard**, classic | No |
| `/environments/<env>/agents/<id>` | **GitHub Copilot harness**, modern | Yes |

`preview.` hostnames behave the same.

---

## The reliable check: ask the environment

Links go stale. The authoritative signal is the recognizer:

| Recognizer | Harness |
|---|---|
| `GenerativeAIRecognizer` | classic, Standard |
| `CLICopilotRecognizer` | modern, GitHub Copilot |

```bash
python3 tools/mcs_skills.py assess --env-url https://YOURORG.crm.dynamics.com --bot-id <guid>
```

Real output, classic:

```
agent      SalesOrderAgent
recognizer GenerativeAIRecognizer
shape      1  (classic, Standard harness)

components (26), by kind
  AdaptiveDialog                  13   classic topic
  AgentDialog                      1   child agent
  ExternalTriggerConfiguration     3
  GptComponentMetadata             1   classic agent
  KnowledgeSourceConfiguration     1   knowledge
  TaskDialog                       7   tool / action
```

Real output, modern:

```
agent      Bank Reconciliation Agent V2
recognizer CLICopilotRecognizer
shape      2  (modern, GitHub Copilot harness)

components (17), by kind
  AgentDialog                      6   child agent
  InlineAgentSkill                 6   skill
  KnowledgeSourceConfiguration     2   knowledge
  McpTool                          1   MCP tool
  TaskDialog                       1   tool / action
```

---

## Do not count components to guess

Both agents above are dominated by `componenttype 9`. Type 9 is a container holding
skills, child agents, tools and classic topics, told apart by `kind`. The classic agent
has *more* type-9 rows than the modern one.

Use the recognizer. Use `kind`. Never use the raw type count.

---

## What differs

| | Modern (`/agents/`) | Classic (`/bots/`) |
|---|---|---|
| `agent.mcs.yml` | **absent, must not be created** | present, `kind: GptComponentMetadata` |
| Instructions | `settings.mcs.yml`, `configuration.agentSettings` | `agent.mcs.yml` |
| Topics | not a concept | `topics/*.topic.mcs.yml` |
| **Skills** | supported, `kind: InlineAgentSkill` | **not available** |
| Knowledge | `capabilities/knowledge/` | `knowledge/*.knowledge.mcs.yml` |
| Actions | `actions/` | `capabilities/tools/` |
| Sandbox | Python execution available | no |

---

## The fail-fast check, corrected

The commonly repeated rule "before authoring, confirm the workspace contains
`agent.mcs.yml`" is true only for classic agents, and is actively wrong for modern ones
where creating that file is the mistake.

- **Classic**: the workspace must contain `agent.mcs.yml`.
- **Modern**: there is no `agent.mcs.yml`. The marker is `settings.mcs.yml` carrying
  `configuration.agentSettings`.

In both cases, if the workspace is not a real clone, do not start writing YAML locally.
Clone the real target first.
