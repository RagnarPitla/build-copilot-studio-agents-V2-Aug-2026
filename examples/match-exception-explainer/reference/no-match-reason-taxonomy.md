# No-match reason taxonomy

Walk this in order. Structural causes come first, because a structural cause makes every
data test below it meaningless. There is no point measuring a tolerance breach on a line the
rule set never even evaluated.

Stop at the first reason that fully explains the line.

## Layer 1. Structural. The rule never had a chance

### MX-01 Rule not activated

| Field | Value |
|---|---|
| Symptom | Nothing matches. No error anywhere |
| Evidence | The rule exists at Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules but was never activated |
| Fix | Open the rule, select Activate |
| Owner | Functional consultant |
| Recurring | Yes, on every statement, until fixed |

The most common cause of "we set it all up and nothing happened". A saved rule is inert and
warns nobody.

### MX-02 Rule not in the account rule set

| Field | Value |
|---|---|
| Symptom | The rule works when run manually, but not on import |
| Evidence | The rule is not a member of the set named as Default matching rule set on the bank account |
| Fix | Add it to the set at Reconciliation matching rule sets, then confirm Default matching rule set on the bank account Reconciliation FastTab |
| Owner | Functional consultant |
| Recurring | Yes |

### MX-03 Transaction code not mapped on this bank account

| Field | Value |
|---|---|
| Symptom | Works on one bank account, not on another |
| Evidence | No mapping row for this statement code at Cash and bank management > Setup > Transaction code mapping for **this** account |
| Fix | Add the mapping row. Read the real code from `Ntry/BkTxCd/Domn/*` or `Ntry/BkTxCd/Prtry/Cd` in the file |
| Owner | Functional consultant |
| Recurring | Yes |

Transaction code mapping is per bank account. It does not carry across accounts. This is the
single most common silent failure in the whole feature.

### MX-04 Parameter override blocks the match

| Field | Value |
|---|---|
| Symptom | The rule looks correct and still does not fire |
| Evidence | Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation. Either Validate transaction type mapping is on with an unmapped line, or the date difference validation is narrower than the rule |
| Fix | Correct the parameter, or correct the rule to sit inside it |
| Owner | Finance lead with the functional consultant |
| Recurring | Yes |

The validation options on the parameters page override the selections on matching rules. You
cannot match beyond the date difference set there, manually or automatically. Check here
before rewriting a rule.

### MX-05 Rule order let a broader rule take the line first

| Field | Value |
|---|---|
| Symptom | The line matched, but to the wrong document |
| Evidence | A broad rule sits above a specific rule in the set. The set runs top to bottom |
| Fix | Reorder at Reconciliation matching rule sets. Most specific first, broadest last |
| Owner | Functional consultant |
| Recurring | Yes |

## Layer 2. Tolerance. The rule ran and the values were too far apart

### MX-06 Amount outside tolerance

| Field | Value |
|---|---|
| Symptom | Amounts are close but not equal, and nothing matched |
| Evidence | The difference between the statement amount and the transaction amount, compared to Allowed penny difference on the bank account Reconciliation FastTab |
| Fix | Widen Allowed penny difference if policy allows, or handle the difference as a residual allocation |
| Owner | Finance lead |
| Recurring | Depends on whether the cause is systematic |

Quote both numbers and the tolerance. Never say "outside tolerance" without the values.

### MX-07 Date outside the permitted difference

| Field | Value |
|---|---|
| Symptom | Same amount, same reference, no match |
| Evidence | Booking date or value date versus the transaction date, against the date difference validation on the parameters page |
| Fix | Widen the date difference, or decide deliberately whether to match on booking date or value date and apply it consistently |
| Owner | Finance lead |
| Recurring | Yes, if the bank consistently books late |

Booking date and value date routinely differ. Choosing one and being consistent removes a
large share of these.

### MX-08 Fee or FX difference makes the amount short

| Field | Value |
|---|---|
| Symptom | Payment received is less than the invoice |
| Evidence | `Ntry/AmtDtls/InstdAmt` greater than `Ntry/Amt`, or a `Ntry/Chrgs` block, or a rate in `CcyXchg/XchgRate` |
| Fix | This is Shape B in `fee-and-fx-posting-advisor`. Tolerance must be wide enough for the match to happen at all, then the residual goes to the fee or FX offset account |
| Owner | Finance lead with the functional consultant |
| Recurring | Yes |

The trap: if the tolerance is narrower than the fee, the line never matches, so the residual
step is never reached, so the fee never posts. The reported symptom is "the fee did not
post". The actual cause is the tolerance.

## Layer 3. Data. The values themselves do not support a match

### MX-09 Reference missing or unusable

| Field | Value |
|---|---|
| Symptom | Nothing to match on except amount |
| Evidence | `RmtInf/Ustrd` empty or truncated, `Refs/EndToEndId` absent |
| Fix | Ask the bank to preserve the full remittance text. Ask the payer to quote the reference. Fall back to an amount and date rule with a tighter tolerance |
| Owner | Bank, or the payer, or accounts receivable |
| Recurring | Yes, for that payer or that channel |

### MX-10 Reference present but matches no open document

| Field | Value |
|---|---|
| Symptom | A reference exists and finds nothing |
| Evidence | The reference value, and the absence of an open document carrying it |
| Fix | Check for a format difference such as a prefix, leading zeros or a campaign code. Do not guess a counterpart |
| Owner | Accounts receivable |
| Recurring | Sometimes |

### MX-11 Counterpart does not exist in D365 yet

| Field | Value |
|---|---|
| Symptom | Money arrived for something not yet entered |
| Evidence | No open transaction of that value in that period |
| Fix | Not a reconciliation problem. The document has to be entered or posted. Alternatively use a Generate customer payment or Generate voucher rule if it never will be an invoice |
| Owner | Accounts receivable or accounts payable |
| Recurring | Depends on process discipline |

### MX-12 Counterpart already settled or already matched

| Field | Value |
|---|---|
| Symptom | Looks like a duplicate payment |
| Evidence | The document is closed, or already matched to a different statement line |
| Fix | Investigate as a possible duplicate receipt, an overpayment, or a duplicate statement, see MX-19 |
| Owner | Finance |
| Recurring | No |

### MX-13 Direction or sign is inverted

| Field | Value |
|---|---|
| Symptom | Everything matches except the sign |
| Evidence | `Ntry/CdtDbtInd` against the ledger direction, and the Reverse debit credit mark setting on the bank account |
| Fix | Set Reverse debit credit mark correctly on the bank account Reconciliation FastTab. Do not fix it per line |
| Owner | Functional consultant |
| Recurring | Yes, on every line of that account |

### MX-14 Line is not a booking

| Field | Value |
|---|---|
| Symptom | A line that should not be reconciled at all |
| Evidence | `Ntry/Sts` is `PDNG` or `INFO` rather than `BOOK` |
| Fix | Exclude non-booked lines. Pending items reconcile when they book |
| Owner | Functional consultant |
| Recurring | Yes |

### MX-15 Reversal pair not recognised

| Field | Value |
|---|---|
| Symptom | Two offsetting lines both sit unmatched |
| Evidence | `Ntry/RvslInd` is set, and no Clear reversal rule exists |
| Fix | Add a Clear reversal statement lines rule for bank errors, or a Clear reversal company transaction rule for our own reversed journals |
| Owner | Functional consultant |
| Recurring | Yes |

## Layer 4. Ambiguity. More than one answer is possible

### MX-16 Multiple candidates match on amount

| Field | Value |
|---|---|
| Symptom | It matched the wrong one, or picked arbitrarily |
| Evidence | More than one open document with the same amount in range |
| Fix | Turn on Require manual matching when advanced bank reconciliation matching rules find multiple documents that match on amount, at Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation. Add a reference criterion to the rule so amount is not the only test |
| Owner | Finance lead with the functional consultant |
| Recurring | Yes, wherever amounts repeat |

By default matching rules match to the first bank document that meets the criteria. For a
nonprofit with many identical donation amounts this is not a corner case, it is the norm.

### MX-17 Split expected, one to many or many to one

| Field | Value |
|---|---|
| Symptom | One transfer covers several invoices, or several transfers cover one |
| Evidence | The statement amount equals the sum of several open documents, or the reverse |
| Fix | Native. Configure the matching rule for the appropriate matching type with suitable tolerances. Hand to `native-reconciliation-config-advisor`. Do not compute the combination in conversation |
| Owner | Functional consultant |
| Recurring | Yes |

Do not present the arithmetic of a candidate combination. Working out which four invoices
add up to the statement amount is performing a match.

## Layer 5. Bank data. The file itself is the problem

### MX-18 Batch booked entry with no per-item detail

| Field | Value |
|---|---|
| Symptom | One large credit representing many payments, nothing to match individually |
| Evidence | `Ntry/NtryDtls/Btch/NbOfTxs` greater than 1, with no per-item `Ntry/NtryDtls/TxDtls` |
| Fix | The detail is not in the file. No configuration recovers it. Ask the bank for detailed booking, or source a separate collection file |
| Owner | Bank, with treasury |
| Recurring | Yes, until the bank changes delivery |

This is the most important check on a high-volume donation account. Verify it before anyone
promises donor-level visibility.

### MX-19 Duplicate statement or duplicate line

| Field | Value |
|---|---|
| Symptom | The same money appears twice |
| Evidence | Repeated statement `Id`, repeated `ElctrncSeqNb`, or repeated `AcctSvcrRef` |
| Fix | Remove the duplicate import. Establish `AcctSvcrRef` as the duplicate key going forward |
| Owner | System administrator |
| Recurring | No, if the import schedule is corrected |

### MX-20 Currency mismatch between line and account

| Field | Value |
|---|---|
| Symptom | Amounts look wrong by an order of magnitude, or nothing matches at all |
| Evidence | `Ntry/Amt` currency attribute against the account currency, and `Acct/Ccy` |
| Fix | Confirm the statement is for the account it was imported into. Check Bank name in statements on multi-account files |
| Owner | Functional consultant |
| Recurring | Yes, if the wrong file is being routed |

## Grouping many exceptions

When reviewing a whole statement, group by reason code and report counts. One configuration
fix usually clears a whole group. Page the read properly. The grid returns 25 rows per call,
so a count from a single page is not a count.

Report in this shape:

| Reason | Count | Value | Fix once or line by line |
|---|---|---|---|
| MX-03 | 41 | Read from a paged total | Fix once, configuration |
| MX-09 | 12 | Read from a paged total | Line by line, plus a request to the bank |
