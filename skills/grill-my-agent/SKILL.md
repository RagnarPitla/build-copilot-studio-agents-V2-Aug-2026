---
name: grill-my-agent
description: Interview the user relentlessly before building or upgrading a Copilot Studio agent, one question at a time, until the design is settled and every behavior has been assigned to the right component. Grills on the real MCP and tool surface, on document samples and templates when the agent ingests documents, and on the business documents describing how the work is done today. Use when the user wants to build an agent, upgrade an agent to the GitHub Copilot harness, mentions "grill me" about an agent, or hands over a Copilot Studio URL with a vague brief.
---

Interview me relentlessly about this agent until we have a design I have actually agreed
to. Walk down the decision tree, resolving dependencies between decisions one at a time.

## When to invoke

Use this before any agent is built or upgraded, including when I hand you nothing but a
Copilot Studio URL. Use it again if the scope changes materially part way through.

Do not use it to fix skills that already exist, that is `grill-my-skills`. Do not use it
for a one-line tweak to an agent that is already designed and running.

## Inputs

You need either a Copilot Studio agent URL or a description of the agent I want. Nothing
else is required from me up front, because everything else is what the interview is for.
If I gave you a URL, the environment and bot GUID come out of it. If the environment is
ambiguous, run `pac env list` and ask me which one rather than guessing.

**Ask one question at a time.** For each question, give me your recommended answer and
say why. I should usually be able to reply "yes" and move on.

**Never ask what you can find out.** If the answer is discoverable, go and discover it
first, then tell me what you found. Specifically, before you ask me anything about an
existing agent:

```bash
pac env list
python3 tools/mcs_skills.py assess --env-url <dataverse-url> --bot-id <guid>
pac copilot clone --bot <guid> --environment <dataverse-url> --output-dir ./source-agent
```

Then read every topic, tool, knowledge source and child agent before your first question.
Do not ask me what my agent does. Tell me what it does, and ask me what still matters.

## Cover these, in this order

Skip any branch that genuinely does not apply, and say you are skipping it.

1. **The job.** Who uses this, and what are they trying to finish? Not "what should the
agent do" but "what does a good day look like for the person using it".

2. **The journeys.** Which handful of paths must work reliably? Get me to name them.
Everything else is a nice-to-have, and naming them now stops scope creep later.

3. **Whether to build this at all.** Ask this while it is still cheap. If the journeys
are Dynamics 365 finance and operations work that spans ERP plus email, documents and
spreadsheets, then say plainly that Microsoft is building **Copilot Cowork** for exactly
that shape of problem, and give me the caveats rather than the headline:

   - It entered public preview in July 2026 with no announced GA date.
   - Preview scope is deliberately narrow: an initial set of finance and supply chain
     scenarios, limited action coverage for transactional workflows, selected customers.
   - It is a release plan, and release plans carry Microsoft's own warning that projected
     functionality may change or may not ship.

   So the recommendation is usually not "wait". It is: build the thing that is specific
   to my business, and do not spend weeks rebuilding generic cross-app orchestration that
   is arriving anyway. Ask me which of our journeys fall on each side of that line.

4. **For an upgrade: what is worth keeping.** Go capability by capability through what
you found. For each one ask: does this still earn its place? Some topics exist because
the old harness needed them, not because anyone wants them. Upgrading is the moment to
drop those, and I will not think of it unless you ask.

5. **Systems.** What must it read from, and what must it write to? Read and write are
very different risk profiles, so separate them explicitly.

6. **The actual tool surface, not the imagined one.** Never design a skill against tools
you assume exist. Ask me which MCP servers and connectors this agent will have, then go
and look at what they really expose before writing a step that calls them.

   If this is Dynamics 365 finance and operations, that is the **Dynamics 365 ERP MCP**
   server, and there are things you must raise with me rather than discover late:

   - It offers three categories: **data tools** for CRUD through data entities, **form
     tools** for what a user can do on a page, and **action tools** that invoke X++
     classes directly. Ask me which category each of our behaviors needs.
   - Microsoft's own guidance is that data tools beat form tools for standard CRUD, on
     both performance and number of tool calls, and that if the agent reaches for form
     tools where data tools would do, you fix it **by naming the preferred tool in the
     agent instructions**. Ask me whether we have scenarios that need that steer.
   - Data tools moved from OData to **SQL**, generally available 24 April 2026. Microsoft's
     stated reason is worth quoting back to me, because it is the whole argument for
     designing skills carefully: OData's limits on aggregation left "much of the data
     aggregation to the agent's large language model rather than deterministic operations
     in the data retrieval". So push aggregation into the query. Do not retrieve rows and
     ask the model to total them, because it will produce a plausible number rather than
     a correct one.
   - If I am upgrading an agent built before that change, look specifically for the
     retrieve-then-let-the-model-add-it-up pattern. That was a workaround for a platform
     limitation that no longer exists, and it is the clearest example of question 8.
   - There is an older **static** ERP MCP server with 13 fixed tools, and it **retires on
     1 October 2026**. If I am upgrading an agent that uses it, tell me that plainly and
     early, because it changes the scope of the upgrade.
   - It needs 10.0.47 or later, a Tier 2 or Unified Developer environment, and our agent
     platform added on the **Allowed MCP Clients** page. Ask me to confirm all three, as
     none of them are visible from the agent itself.

   For any other MCP or connector, ask the same underlying question: what does it
   actually expose, what does it require, and what does it refuse to do?

7. **Documents in.** If the agent ingests documents, ask me for real samples before
writing anything, and say why you are asking: a skill written against an imagined layout
will look right and fail on my actual files.

   Ask for the awkward ones too, not the tidy example. The multi-page one, the scanned
   one, the one from the vendor who formats everything differently, the one in the wrong
   language. Then ask what happens when a document does not fit any known template,
   because that is the case that will otherwise get silently mishandled.

   Ask which fields must be extracted exactly and which can be inferred. Anything that
   must be exact and then arithmetic on top of it belongs in a script, not in prose.

8. **How the work is done today.** Ask me for the real business documents: the SOP, the
work instruction, the policy, the checklist someone keeps in a spreadsheet. These carry
the rules and exceptions nobody thinks to mention in an interview, and they are usually
the difference between an agent that demos and an agent that survives.

   Then do the part I am not asking for. Having read them, tell me where the current
   process is a workaround for an old system limitation rather than a genuine business
   rule. Do not simply automate the current mess faster. Propose the better way, say
   what it would change for the people doing the work, and let me decide. Be clear about
   which parts of your proposal are grounded in the documents and which are your opinion.

9. **The blast radius.** What must never happen without me confirming first? Anything
that posts, books, sends, approves or deletes needs an explicit confirmation rule, and
that rule belongs in the skill that does it.

10. **Where each behavior belongs.** This is the part that decides whether the agent is
any good. For every behavior we have named, put it in exactly one place, and tell me
which and why:

- always true in every conversation, no exceptions, then **instructions**
- I need it searched or cited, then **knowledge**
- one system call, then a **tool**
- a procedure with steps, inputs and confirmations, then a **skill**
- must survive across conversations, then **memory**
- a genuine specialist domain with its own remit, then a **connected agent**

Push back on me if I try to put everything in instructions. That is the most common
failure and it produces an agent nobody can debug.

11. **Anything needing exact arithmetic or a real file.** Totals, reconciliations,
variances, a valid `.docx` or `.xlsx`. Models predict plausible numbers rather than
computing correct ones, so these become a skill carrying a Python script that the
sandbox runs. Ask me which of our behaviors are in this category.

12. **What correct looks like.** Get three or four concrete examples out of me: an input,
and the response I would accept. These become the test cases, and without them neither
of us can tell whether the build worked.

13. **Cost and permissions.** Tell me, do not ask: the GitHub Copilot harness bills in
Copilot Credits and starts charging while we build, not at publish. Then ask whether I
want to keep the scope tight for that reason.

## Before you stop

Show me a single table: every behavior, the component it lands in, and one line of
justification. Plus the list of skills you intend to write, each with its one-sentence
routing description.

Ask me to approve that table. Do not write a single file until I have.

If I tell you to just get on with it, then stop asking, state every assumption you are
making as a numbered list, and proceed. Mark that list clearly so I can review it later,
because I will.
