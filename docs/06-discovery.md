# The discovery questions

`skills/grill-my-agent/SKILL.md` is the runnable version. This is the wording behind it,
for when you want to run the conversation yourself, or check whether the agent skipped
something it should have asked.

Three rules make the difference between an interview and an interrogation.

**One at a time.** A wall of twelve questions gets one vague answer covering three of them.

**Always bring your own answer.** Every question below should arrive as "here is what I
would do and why, does that hold?" The user should usually be able to say yes. Asking an
expert to fill in a blank form wastes the expertise.

**Never ask what you can find out.** For an existing agent that means `assess`, then
`pac copilot clone`, then reading every topic and tool, before the first question. Do not
ask someone what their own agent does.

---

## Round 1: the job

Ask these before anything technical. If you get them wrong the rest is wasted.

- Who uses this, and what are they in the middle of when they open it?
- What does a good day look like for them? Not what the agent does, what they get to stop doing.
- What are the handful of paths that must work? Everything else is a nice-to-have, and naming them now is what stops scope creep later.
- What happens today when it goes wrong, and who picks it up?
- How will you know in a month whether this was worth building?

## Round 2: is this the right thing to build

Cheap to ask now, expensive to discover later.

- Is any of this something Microsoft is already shipping? For cross-app finance and operations work, say what you know about Copilot Cowork, including that it is preview with narrow scope, and let them decide.
- Is any of this better as a change to the underlying system than as an agent on top of it?
- Which of these journeys is specific to your business, and which is generic? Spend the effort on the specific ones.

## Round 3: for an upgrade only

Go capability by capability through what you found in the clone. For each one:

- Does this still earn its place, or did it exist because the old harness needed it?
- Who actually uses this topic? Some exist because someone asked once, three years ago.
- Was this built around a platform limitation that no longer applies? The clearest example in finance and operations is retrieving rows and letting the model add them up, which was a workaround for OData's aggregation limits and is now handled in SQL.
- What annoys people about the current agent? Upgrading is the only moment they will be asked.

## Round 4: the tool surface

Never design against tools you assume exist.

- Which MCP servers and connectors will this agent have? Then go and read what they actually expose.
- For Dynamics 365 finance and operations: which behaviors need data tools, which need form tools, and which need action tools?
- Are we on 10.0.47 or later, a Tier 2 or Unified Developer environment, with our agent platform on the Allowed MCP Clients page? None of this is visible from the agent itself.
- Does anything here still depend on the static ERP MCP server? It retires on 1 October 2026.
- What does the tool refuse to do? That constraint shapes the skill more than what it allows.

## Round 5: documents

Only if the agent ingests documents, but then ask all of it.

- Can I have real samples before I write anything? A skill written against an imagined layout looks right and fails on your files.
- Can I have the awkward ones too? The multi-page one, the scanned one, the vendor who formats everything differently, the one in the wrong language.
- Which fields must be extracted exactly, and which can be inferred?
- What should happen when a document matches no known template? This is the case that otherwise gets silently mishandled.
- Where do the documents come from, and does anyone check them before the agent sees them?

## Round 6: how the work is done today

- Can I have the SOP, the work instruction, the policy, or the checklist someone keeps in a spreadsheet? These carry the exceptions nobody thinks to mention.
- Walk me through the last time this went wrong.
- Who reviews this today, and what are they actually checking for?

Then do the part nobody asked for. Having read them, say where the current process is a
workaround for an old system limitation rather than a genuine business rule. Propose the
better way, say what it would change for the people doing the work, and be explicit about
which parts of the proposal are grounded in the documents and which are your opinion.

Automating a broken process faster is the most common way these projects disappoint.

## Round 7: blast radius

- What must never happen without someone confirming first?
- Which of these actions can it take on its own?
- What is the worst thing this could plausibly do, and what would that cost?
- Who is accountable when it does something wrong?

Anything that posts, books, sends, approves or deletes needs a confirmation rule written
into the skill at the point it happens, not as a general warning at the top.

## Round 8: where each behavior goes

For every behavior named so far, place it in exactly one component and say why.

| If it is | It belongs in |
|---|---|
| Always true, every conversation | Instructions |
| Something to search, ground in, or cite | Knowledge |
| One system call | A tool |
| A procedure with steps, inputs and confirmations | A skill |
| Context that must survive the conversation | Memory |
| A genuine specialist domain with its own remit | A connected agent |

Push back when everything lands in instructions. That is the most common failure and it
produces an agent nobody can debug.

Ask separately: which of these needs exact arithmetic or a real file? Totals,
reconciliations, variances, a valid `.docx`. Those become a skill carrying a Python
script, because a model predicts plausible numbers rather than computing correct ones.

## Round 9: what correct looks like

- Give me three or four real examples: what someone types, and the response you would accept.
- Give me one where the right answer is "I cannot do that" or "you need a human".
- What answer would embarrass you in front of a customer?

Without these, nobody can tell whether the build worked, and there is nothing to refine
against after deployment.

## Round 10: cost and permissions

State these, do not ask.

- The GitHub Copilot harness bills in Copilot Credits, and starts charging while you build, not at publish.
- Consumption shows on the agent's Monitor tab.

Then ask the one real question: does that change how tightly you want to scope this?

---

## Stopping

You are done when you can show one table with every behavior, the component it lands in,
and one line of justification, and the user has approved it. Not before.

If they tell you to get on with it, stop asking, but write every assumption as a numbered
list first so it can be reviewed later.
