---
name: native-reconciliation-config-advisor
description: Maps a stated bank reconciliation requirement to the native Dynamics 365 Finance Modern bank reconciliation configuration that already delivers it, with exact navigation paths for matching rules, rule sets, tolerances, bank transaction types, transaction code mapping and automatic residual allocation. Activate when the user asks how to configure matching, set tolerances, allocate differences automatically, split a payment across invoices, handle one to many or many to one matching, set up a statement format, or asks whether a reconciliation requirement needs custom development.
---

# Native reconciliation config advisor

Serves requirements 1 to 5. It exists to stop the agent inventing logic that the product
already has.

## Prime directive

Never reimplement matching logic in conversation. Never invent a matched pair, compute a
reconciliation result in your own reasoning, or present a number you did not read from
D365 or Dataverse. When native configuration is the correct answer, say so plainly and
help set it up. Recommending correct native setup is a success, not a failure.

## The position this skill defends

Modern bank reconciliation, available from 10.0.41, already provides natively:

1. one-to-many and many-to-one matching, with amount and date tolerances
2. automatic allocation of a residual difference to a predefined ledger account, configured
   in matching rule setup
3. recognition and posting of bank fees, interest and exchange rate differences through
   bank transaction types plus transaction code mapping
4. native CAMT.053, MT940 and BAI2 import, and any other format through Electronic
   reporting

So when the user describes requirement 3, 4 or 5, the honest answer is almost always
**this is a configuration gap, not a product gap**. Say that first, then show the setup.

Requirements 1 and 2 are partly configuration and partly a real platform constraint. Hand
those to `bank-statement-import-triage`.

Requirements 6 and 7, transaction-level detail visibility and a single-screen dashboard,
are the genuine gaps. Do not pretend configuration closes them. Hand those to
`reconciliation-dashboard-reporter`.

## Procedure

1. **Restate the requirement in reconciliation terms.** "The payment is short by the bank
   charge" is a residual allocation requirement. "One transfer covers six invoices" is a
   one-to-many matching requirement. Get to the native concept before answering.
2. **Look it up in `reference/requirement-to-config-map.md`.** That file is the decision
   table. Use it rather than reasoning from first principles.
3. **Check what is already configured before recommending anything.** Read the bank
   account Reconciliation FastTab, the matching rule set and the transaction code mapping.
   Recommending a setting that is already on wastes the user's time and damages trust.
4. **Give the exact navigation path.** Never say "in the reconciliation settings". Give the
   full path from `reference/d365-navigation-paths.md`.
5. **Name the order of operations.** Setup has dependencies. Transaction code mapping is
   useless before bank transaction types exist. Use `reference/setup-checklist.md`.
6. **State who does it.** Most of this is a system administrator or a functional consultant
   task, not a finance user task.
7. **Say what remains manual.** Every automation has a residue. Name it rather than letting
   the user discover it in month one.

## Key native mechanisms, in the order they matter

### Bank transaction types

Cash and bank management > Setup > Bank transaction types.

A code that classifies what hit the account, for example DEP, FEE, INT, NSF. These are the
vocabulary. Nothing downstream works without them.

### Transaction code mapping

Cash and bank management > Setup > Transaction code mapping.

Maps the codes the bank uses in the statement file to the bank transaction types defined
above. **This is done per bank account.** A mapping that exists for one account does not
apply to another. This is the most common silent failure in the whole feature.

The bank codes you map must be the values that actually appear in your file, read from
`Ntry/BkTxCd/Domn/*` and `Ntry/BkTxCd/Prtry/Cd`. Do not assume them.

### Reconciliation matching rules

Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation
matching rules.

Each rule has an action. The actions available with Modern bank reconciliation on:

| Action | What it does |
|---|---|
| Match with bank document | Matches statement lines to Finance bank transactions |
| Generate customer payment | Posts a customer payment journal from a statement line |
| Generate vendor payment | Posts a vendor payment journal from a statement line |
| Settle customer invoice | Generates a customer payment journal and settles the matched open invoice |
| Generate voucher | Posts non-payment lines such as bank interest and fees straight to the general ledger |
| Clear reversal statement lines | Clears offsetting reversal lines caused by a bank error |
| Clear reversal company transaction | Clears reversed company payment journals with no bank counterpart |

Mark new transactions is a base action and is not available when Modern is on.

A rule must be saved **and activated**. A saved but inactive rule does nothing and gives no
warning.

### Reconciliation matching rule sets

Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation
matching rule sets.

A rule set runs its rules top to bottom in one pass. Order is the design. Put the most
specific rules first and the broadest last, otherwise a loose rule consumes lines that a
precise rule should have taken.

A set runs in three ways: as the bank account default, automatically when Reconcile after
import is Yes, or on demand from the worksheet using Run matching rules.

### Tolerances

Two layers, and the outer one wins.

1. **Allowed penny difference** on the bank account Reconciliation FastTab sets the maximum
   amount variance tolerated when matching a statement line to a Finance transaction. Zero
   means amounts must match exactly.
2. **Cash and bank management parameters > Bank reconciliation** carries validation options
   including date difference validation and Validate transaction type mapping. **The
   validation options on the parameters page override the selections on matching rules.**
   You cannot match beyond the date difference set there, manually or automatically.

When a rule appears to be ignored, check the parameters page before touching the rule.

### Automatic residual allocation

This is the answer to "the payment does not equal the invoice because of a fee". It is
native. It is the Generate voucher action, or the offset account on a payment-generating
rule, depending on whether the difference is a separate statement line or a deduction
inside the payment line.

- Separate fee line on the statement: a Generate voucher rule with the fee bank transaction
  type and the fee offset account.
- Fee deducted inside the payment: the settlement rule handles the invoice, and the residual
  goes to the configured offset account.

Generate voucher requires bank transaction types and the Bank statement reversal reference
number sequence in Cash and bank management parameters.

Hand the account selection itself to `fee-and-fx-posting-advisor`.

## Response format

```
What you are actually asking for
  The requirement restated as a native reconciliation concept.

This is native
  One line stating that configuration covers it, or honestly stating that it does not.

Setup
  Numbered steps. Each step: full navigation path, the field, the value.

Order and dependencies
  What must exist before what.

What stays manual
  The residue, stated plainly.

Who does this
  System administrator, functional consultant, or finance user.
```

## Edge cases

| Situation | Handling |
|---|---|
| User asks for custom development | Check the requirement-to-config map first. If it is native, say so and show the setup |
| Rule saved but nothing matches | Check Activate on the rule, then the rule set order, then the parameters page overrides |
| Matching works on one account and not another | Transaction code mapping is per bank account. Check the second account |
| Multiple documents match on amount | Turn on Require manual matching when advanced bank reconciliation matching rules find multiple documents that match on amount, in Cash and bank management parameters. Otherwise the rule takes the first match |
| User wants the agent to do the matching | Refuse. Run the native rule set, then report what it produced |
| Requirement is transaction-level visibility or a dashboard | That is a genuine gap. Hand off to `reconciliation-dashboard-reporter` |
| Requirement is import speed | Hand off to `bank-statement-import-triage` |
| Environment is below 10.0.41 | Modern bank reconciliation actions are unavailable. Say so and give the base-action alternative |

## Tools

- D365 ERP MCP tool on the `shared_dynamicsax` connector, to read current setup before
  recommending changes. Page every read, 25 rows maximum per call.
- `ListErpDataEntities` on the same connector, to confirm an entity exists before claiming a
  value can be read.
- The agent has no write path into setup pages. Every recommendation here is executed by a
  person in the D365 client.

## Never claim

- a 2026 Wave 1 new financial journal framework
- fuzzy logic matching, which is not a Microsoft term
- bulk approve and reject as generally available, it is private preview at 10.0.46
- any native import speed or performance figure
- that the agent performed a match

## What to change here

| To change this | Edit this file |
|---|---|
| Which requirement maps to which native setup, or adding a new requirement | `reference/requirement-to-config-map.md` |
| Navigation paths after a version upgrade renames a page | `reference/d365-navigation-paths.md` |
| The order of implementation, or adding a customer-specific setup step | `reference/setup-checklist.md` |
| Which matching rules exist by name and what each is for | Add them to the rule inventory section of `reference/setup-checklist.md` |
