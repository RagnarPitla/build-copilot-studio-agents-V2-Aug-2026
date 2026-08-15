# The skill quality bar

A skill that is valid will deploy. A skill that is good will fire on the right request,
refuse the wrong one, and behave the same way next week. Those are different things, and
only the first one is checkable by a machine.

```bash
python3 tools/mcs_skills.py validate --path ./skills          # warnings are advisory
python3 tools/mcs_skills.py validate --path ./skills --strict # warnings fail the run
```

Errors block deployment. Warnings do not, because a warning is a judgement call and the
tool cannot make it for you. Use `grill-my-skills` to turn each one into a question for
whoever knows the domain.

## The rubric

Eight checks, and what each one is really asking.

| Check | The question behind it |
|---|---|
| Routing description under 60 characters | The orchestrator matches on this and nothing else. Short means it never fires, or fires on everything |
| Description never says when to use it | A description that lists capabilities but no trigger cannot be matched against a user's request |
| No "when to invoke" section | Without a stated boundary, two skills will fight over the same request and you will not see which won |
| No inputs section | If required information is undefined, the model will invent a plausible value rather than ask |
| No ordered steps | Prose gets skimmed. A procedure gets followed |
| No failure handling | An agent with no failure path improvises one, confidently |
| Side effects but no confirmation | It posts, books, sends or deletes, and nothing tells it to stop and ask |
| Body under 400 characters | A few lines of always-true guidance belongs in instructions. A skill earns its place by being a procedure |

There is a ninth for bodies over 12,000 characters, which usually means two skills wearing
one coat.

## What the checker cannot see

The failures that actually hurt are all invisible to it.

**Two descriptions that overlap.** Read them side by side. If you cannot say which should
win, they are one skill.

**A skill that overlaps a connected agent.** Same problem, worse, because the orchestrator
picks one and you will not easily see which.

**Arithmetic in prose.** "Calculate the total variance" tells the model to predict a
number. Deterministic work belongs in a script the sandbox runs. Microsoft made this exact
argument when moving ERP data tools from OData to SQL: the point was to stop leaving
aggregation to the language model.

**Claims about the platform.** If a skill asserts what the product can or cannot do, ask
how you know. Unverified claims sound authoritative and get repeated to customers.

**Instructions wearing a skill costume.** If it never has steps and never touches a
system, it is guidance. Move it.

## A worked rewrite

The weak version, which passes validation and fails in production:

```markdown
---
name: invoice-helper
description: Handles invoices.
---

# Invoice helper

This skill deals with invoices. It will post them to the ledger and update records.
```

Eight warnings, and every one of them is a real defect. "Handles invoices" cannot be
matched against anything a user would actually type. There is no boundary, so it collides
with every other finance skill. Nothing says what it needs, so it will invent an invoice
number. Nothing says what to do when the vendor does not exist. And it posts to the
ledger with no confirmation anywhere, which is the one line in the file that should have
been hardest to write.

The rewrite, after asking the questions the warnings imply:

```markdown
---
name: vendor-invoice-posting
description: Post a vendor invoice to the ledger in Dynamics 365 finance and
  operations after matching it to a purchase order. Use when someone asks to post,
  book or record a vendor invoice, or asks why an invoice has not posted. Not for
  customer invoices or for credit notes.
---

# Vendor invoice posting

## When to invoke

Use for a vendor invoice that needs matching and posting.

Do not use for customer invoices, credit notes, or a question about an invoice that
has already posted. Those are read-only lookups and belong elsewhere.

## Inputs

Required: vendor account, invoice number, invoice date, gross amount, currency.
Optional: purchase order number, which speeds up matching.

If any required value is missing, ask for it. Never infer an invoice number or an
amount, and never round a currency value to make a match work.

## Steps

1. Retrieve the vendor and confirm the account is active. Stop if it is not.
2. Find candidate purchase orders. Prefer the data tools over the form tools, they
   are faster and take fewer calls for this.
3. Match line by line. Aggregate in the query, not in your own reasoning.
4. If the totals differ, do not adjust anything. Show the user the difference,
   the lines involved, and the likely cause.
5. Show the proposed posting in full: accounts, amounts, dates, currency.
6. Ask for explicit confirmation. Wait for it.
7. Post only after the user confirms. Report the voucher number.

## When it goes wrong

- Vendor not found, or on hold: stop and say so. Do not create the vendor.
- No matching purchase order: show what you searched, and offer a non-PO posting
  as a separate confirmed step.
- Totals do not agree: show the gap, never split the difference silently.
- The posting call fails: report the error verbatim. Never retry a posting.
```

What actually changed. The description now names the trigger, the system, and the
boundary, which is the single edit most likely to change behavior. The negative examples
in "when to invoke" stop it colliding with the read-only skills. Inputs are explicit,
including the instruction not to infer. Confirmation sits at step 6, where it happens,
rather than as a warning at the top that gets rationalised away. Failures are enumerated,
including the two that matter most: never invent a vendor, never retry a posting.

## Where the loop closes

A clean `--strict` run means the skills are well formed. It does not mean they are
correct. Run them against the concrete examples from discovery, fix what misfires, and
re-test. Routing problems live in the description. Wrong answers live in the body.

The two skills in `skills/` failed this rubric on first write and were rewritten until
`--strict` was clean. That is not a boast, it is the expected number of passes.
