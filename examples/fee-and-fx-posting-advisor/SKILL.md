---
name: fee-and-fx-posting-advisor
description: Explains how bank charges, interest, service charges, wire transfer fees and exchange rate gains or losses are recognised and posted in Dynamics 365 Finance, and checks that the written policy and the actual bank transaction type and transaction code mapping agree. Activate when the user asks about bank fees, deducted charges, short payments caused by fees, FX differences, exchange rate gain or loss, which ledger account a charge should hit, or why a fee was posted to the wrong account or not posted at all.
---

# Fee and FX posting advisor

Serves requirement 3 (allocation of differences to bank fee and exchange rate difference
accounts) and requirement 4 (automatic detection and calculation of bank charges and FX
differences).

## Prime directive

Never reimplement matching logic in conversation. Never invent a matched pair, compute a
reconciliation result in your own reasoning, or present a number you did not read from
D365 or Dataverse. When native configuration is the correct answer, say so plainly and
help set it up. Recommending correct native setup is a success, not a failure.

## The central point of this skill

There are two layers, and **both must agree or automation silently fails**.

| Layer | What it is | Where it lives | What happens if it is wrong |
|---|---|---|---|
| **Policy** | The governance decision. Which fee types are recognised, what account each belongs in, what may post automatically, above what value a human approves | `templates/fee-and-fx-posting-matrix.csv`, and ultimately the `br_auto_posting_rule` policy table | The posting is technically valid and financially wrong. Nobody notices until audit |
| **Recognition and posting** | The mechanical layer. Which statement code becomes which bank transaction type, and which rule posts it to which account | Bank transaction types, Transaction code mapping, and the Generate voucher matching rule | Nothing posts, or it posts to a default account. The line sits unmatched |

Policy is the governance layer. Actual recognition and posting is driven by bank
transaction types plus transaction code mapping. Policy alone changes nothing in the
system. Mapping alone is ungoverned.

**The failure mode is silent.** A fee with a policy entry but no transaction code mapping
simply never posts, and the statement line stays unmatched with no error. A fee with a
mapping but no policy entry posts to whatever the rule says, which may be the wrong
account, and produces no warning at all. Always check both layers. Say which one is broken.

## Recognition is native, not something to build

Requirement 4 is a configuration gap, not a product gap. Modern bank reconciliation
recognises and posts bank fees, interest and exchange rate differences natively through:

1. **Bank transaction types** at Cash and bank management > Setup > Bank transaction types.
   The vocabulary. FEE, INT, SVC, WIRE, FXDIFF and so on.
2. **Transaction code mapping** at Cash and bank management > Setup > Transaction code
   mapping. Maps the bank's statement codes to those types. **Per bank account.**
3. **A Generate voucher matching rule** at Cash and bank management > Setup > Advanced bank
   reconciliation setup > Reconciliation matching rules. Posts non-payment lines such as
   interest and fees straight to the general ledger, using the bank transaction type and an
   offset account.

Generate voucher requires the Modern bank reconciliation feature, bank transaction types,
and the Bank statement reversal reference number sequence in Cash and bank management
parameters.

Say this before offering anything else. Do not design a workaround for a feature that
exists.

## Two different shapes of fee

Diagnose which one you are looking at first. They have different fixes.

### Shape A. The fee is its own statement line

The bank booked the charge separately. The payment line is clean.

- Fix: a Generate voucher rule that finds fee lines by bank transaction type and posts them
  to the bank fee account with the correct offset account.
- Evidence: a separate `Ntry` in the statement with a fee transaction code.

### Shape B. The fee is deducted inside the payment

The payment arrives short. There is no separate fee line.

- Fix: the settlement rule handles the invoice, and the residual difference goes to the
  configured offset account. Tolerances must be wide enough to allow the match in the first
  place, or the line never reaches the residual step.
- Evidence: `Ntry/AmtDtls/InstdAmt` greater than `Ntry/Amt`, and often a `Chrgs` block.

The arithmetic, when the bank provides it:

```
InstdAmt (gross)  -  TtlChrgsAndTaxAmt (fees)  =  Ntry/Amt (net booked)
```

If `Chrgs/Rcrd/ChrgInclInd` is true, the charge is already inside the booked amount. Do not
subtract it again. Double-counted fees usually start here.

If the bank sends no `AmtDtls` and no `Chrgs`, the gross amount and the fee breakdown are
not in the file. The difference can still be derived by comparing the booked amount to the
open invoice, but **that is a derived figure, not a bank-reported one**. Label it as
derived. Never present a derived number as if the bank stated it.

## FX differences

An FX difference is not a fee, and mixing them up misstates both accounts.

| Situation | What it is | Where it posts |
|---|---|---|
| Bank converted at a rate different from the rate used on the invoice | Realised exchange rate difference | FX gain or FX loss account |
| Bank charged a conversion or handling fee on top of the conversion | Bank charge | Bank fee account |
| Both happened on the same payment | Both, separately | Split them. Do not net them into one line |

The bank's applied rate is in `Ntry/AmtDtls/CntrValAmt/CcyXchg/XchgRate` when supplied, with
`SrcCcy` and `TrgtCcy`. If it is not supplied, say so rather than back-calculating a rate
and presenting it as the bank's rate.

Realised FX difference on settlement is produced by the payment settlement itself using the
exchange rate setup in the ledger, not by the reconciliation rule. The reconciliation rule
handles a residual that settlement did not absorb. Keep those two straight when explaining
where a number came from.

## Procedure

1. **Identify the fee type.** Bank charge, interest, service charge, wire transfer fee, FX
   gain or loss, or other. Use the row labels in `templates/fee-and-fx-posting-matrix.csv`.
2. **Identify the shape.** Separate line, or deducted inside the payment.
3. **Check layer 2 first, the mapping.** Is there a bank transaction type for it. Is there a
   transaction code mapping row on **this specific bank account**. Read the actual statement
   code from the file rather than assuming it.
4. **Check layer 1, the policy.** Is there a row in the posting matrix. Does it name a
   ledger account, an offset account, a journal and an approval threshold.
5. **Compare the two.** Report which layer disagrees. This is the whole value of the skill.
6. **Give the fix with the exact path.** Never say "in the fee settings".
7. **State the approval consequence.** If the amount exceeds the maximum auto-post amount in
   the matrix, say it needs approval before posting rather than letting it post silently.

## Response format

```
What this charge is
  Fee type and shape, in one line.

Where it should post
  Ledger account and offset account, quoted from the posting matrix,
  naming the file and row you read it from.

Why it is not posting, or posted wrongly
  Which of the two layers is broken. Be specific.

Fix
  Numbered steps with full navigation paths.

Approval
  Whether this amount can post automatically under current policy.
```

If you read an amount from D365, state the record it came from. If you derived an amount,
say the word derived.

## Edge cases

| Situation | Handling |
|---|---|
| Fee has a policy row but no transaction code mapping | It will never post. The line stays unmatched with no error. Say so plainly |
| Fee has a mapping but no policy row | It posts to whatever the rule says, possibly the wrong account, with no warning. Flag it |
| Mapping exists on one bank account but not another | Transaction code mapping is per bank account. This is the most common silent failure |
| Charge already included in the booked amount | Check `ChrgInclInd`. Do not subtract twice |
| Bank sends no fee detail at all | The breakdown is not in the file. Request it from the bank. Any figure you produce is derived and must be labelled as such |
| FX and fee on the same payment | Split them across the FX account and the fee account. Never net them |
| Amount exceeds the auto-post threshold | Route to approval. Do not describe it as automatic |
| User asks the agent to post the adjustment | The agent does not post. Configure the rule, or a person posts from the worksheet |
| Statement code is missing from the file entirely | No mapping can be built. Escalate to the bank |
| User asks for a total of fees this month | Only from a full paged read. The grid returns 25 rows per call. Never total from one page |

## Tools

- D365 ERP MCP tool on the `shared_dynamicsax` connector, to read statement lines, bank
  transaction types, transaction code mapping and posted vouchers. Page every read, 25 rows
  maximum per call.
- `ListErpDataEntities` on the same connector, to confirm an entity exists before claiming a
  field can be read.
- No Dataverse tool is wired to this agent. Policy in `br_auto_posting_rule` cannot be read
  at runtime. Use the shipped templates as the policy of record and say that is what you
  are quoting.

## Never claim

- that a fee posted, unless you read the voucher
- a rate the bank did not supply
- a 2026 Wave 1 new financial journal framework
- fuzzy logic matching, which is not a Microsoft term
- bulk approve and reject as generally available, it is private preview at 10.0.46
- any native import speed or performance figure

## What to change here

| To change this | Edit this file |
|---|---|
| Which bank statement code becomes which bank transaction type, per bank account. **The single most customer-specific artifact in the solution** | `templates/transaction-code-mapping.csv` |
| Which ledger account, offset account and journal each fee type posts to, and the auto-post ceiling | `templates/fee-and-fx-posting-matrix.csv` |
| How fee shapes are diagnosed, and the silent failure checks | `reference/fee-and-fx-decision-guide.md` |
| Adding a new fee type | Add a row to both templates. A row in only one of them is exactly the silent failure this skill exists to catch |
