# Evidence checklist

What to read before stating a reason. Diagnosing from the user's paraphrase produces
confident wrong answers.

Rule: quote the values you read and name where each came from. If you did not read it, do
not state it.

## Always read first

| Item | Source |
|---|---|
| Statement line identifier | Bank statement line |
| Amount and currency | `Ntry/Amt` with its `Ccy` attribute |
| Credit or debit indicator | `Ntry/CdtDbtInd` |
| Booking date | `Ntry/BookgDt/Dt` |
| Value date | `Ntry/ValDt/Dt` |
| Status | `Ntry/Sts`. Only `BOOK` is reconcilable |
| Reversal indicator | `Ntry/RvslInd` |
| Bank transaction code | `Ntry/BkTxCd/Domn/*` and `Ntry/BkTxCd/Prtry/Cd` |
| Bank reference | `Ntry/AcctSvcrRef` |
| Which worksheet tab the line sits on | Bank reconciliation worksheet, Unmatched or Matched |

Confirming which tab the line is on takes one read and prevents the whole class of "it is
actually matched, just not to what they expected".

## Structural checks, for MX-01 to MX-05

| Item | Where |
|---|---|
| Does the rule exist and is it activated | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules |
| Is the rule in the set | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rule sets |
| Which set is the account default | Bank account > Reconciliation FastTab > Automation > Default matching rule set |
| Rule order within the set | Reconciliation matching rule sets |
| Is there a transaction code mapping row for this code on this account | Cash and bank management > Setup > Transaction code mapping |
| Does the bank transaction type exist | Cash and bank management > Setup > Bank transaction types |
| Validate transaction type mapping setting | Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation |
| Date difference validation setting | Same page |
| Require manual matching on multiple amount matches | Same page |

## Tolerance checks, for MX-06 to MX-08

| Item | Where |
|---|---|
| Allowed penny difference | Bank account > Reconciliation FastTab |
| The actual amount difference | Statement amount minus candidate transaction amount. State both numbers |
| The actual date difference in days | Booking date or value date minus transaction date. State both dates |
| Gross instructed amount | `Ntry/AmtDtls/InstdAmt/Amt` |
| Total charges | `Ntry/Chrgs/TtlChrgsAndTaxAmt` |
| Charge already included flag | `Ntry/Chrgs/Rcrd/ChrgInclInd` |
| Exchange rate applied | `Ntry/AmtDtls/CntrValAmt/CcyXchg/XchgRate` |

Always quote the difference and the tolerance together. "Outside tolerance" with no numbers
is not a diagnosis.

## Data checks, for MX-09 to MX-15

| Item | Where |
|---|---|
| End-to-end reference | `Ntry/NtryDtls/TxDtls/Refs/EndToEndId` |
| Mandate reference for direct debits | `Refs/MndtId` |
| Unstructured remittance text | `RmtInf/Ustrd` |
| Structured creditor reference | `RmtInf/Strd/CdtrRefInf/Ref` |
| Payer name | `RltdPties/Dbtr/Nm` |
| Payer IBAN | `RltdPties/DbtrAcct/Id/IBAN` |
| Additional entry text | `Ntry/AddtlNtryInf` |
| Whether an open document with that reference exists | D365 open customer or vendor transactions |
| Whether the candidate is already settled or matched | D365 transaction status |
| Reverse debit credit mark setting | Bank account > Reconciliation FastTab |

## Ambiguity checks, for MX-16 and MX-17

| Item | Where |
|---|---|
| How many open documents sit in the amount range | D365 open transactions, paged |
| Whether the statement amount equals a sum of several documents | Observe that it is a split situation. **Do not compute or present the combination** |
| Require manual matching parameter state | Cash and bank management parameters > Bank reconciliation |

Identifying that a split is involved is diagnosis. Naming which documents form the split is
matching. Stop at diagnosis.

## Bank data checks, for MX-18 to MX-20

| Item | Where |
|---|---|
| Batch transaction count | `Ntry/NtryDtls/Btch/NbOfTxs` |
| Batch total | `Ntry/NtryDtls/Btch/TtlAmt` |
| Whether per-item detail exists | Presence of `Ntry/NtryDtls/TxDtls` per item |
| Statement identifier | `Stmt/Id` |
| Electronic sequence number | `Stmt/ElctrncSeqNb` |
| Account currency | `Stmt/Acct/Ccy` |
| Bank name in statements setting | Bank account > Reconciliation FastTab |

## Paging rules

The MCP grid returns a maximum of 25 rows per call. This is not negotiable and it changes
what you are allowed to say.

1. Any count, sum or total must come from a fully paged read. Say how many pages you read.
2. If you could not complete the paging, say the figure is partial and say what you covered.
3. Never present a first page as a summary of the statement.
4. Prefer a statement header balance over a computed total when one is available.
5. When grouping exceptions by reason, the group counts are subject to the same rule.

## Phrases to avoid

| Do not say | Say instead |
|---|---|
| This is the payment for invoice INV-4417 | This line carries no usable reference, so the reference test could not run |
| It should match to these four invoices | This looks like a one-to-many situation. Configure the matching rule for it |
| The total unmatched is 18,400 | Across the 3 pages I read, the unmatched value is 18,400. State the coverage |
| Roughly | The number you read, or nothing |
| I have matched it | The native rule set matches. I can explain why it did not |
