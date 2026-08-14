# Fee and FX decision guide

How to diagnose a fee or exchange rate difference, and how to catch the two silent failure
modes.

## Step 1. Which shape is it

| Question | Shape A, separate line | Shape B, deducted inside the payment |
|---|---|---|
| Is there a dedicated statement entry for the charge | Yes | No |
| Does the payment line equal the invoice | Yes | No, it is short |
| Is `Ntry/AmtDtls/InstdAmt` present and larger than `Ntry/Amt` | Not relevant | Usually yes |
| Is there a `Ntry/Chrgs` block | Sometimes | Usually yes |
| Native mechanism | Generate voucher matching rule | Settlement rule plus residual to the offset account |
| First thing that breaks it | No transaction code mapping for the fee code | Tolerance too tight, so the line never matches at all |

Shape B has an important trap. If the tolerance is narrower than the fee, the payment never
matches, so the residual step is never reached, so the fee never posts. The reported
symptom is "the fee did not post" but the actual cause is the tolerance. Check the tolerance
before touching the fee setup.

## Step 2. Which fee type is it

| Type | Recognise it by | Account family |
|---|---|---|
| Bank Fee | Charge on a specific transaction or a general charge line | Bank charges expense |
| Interest | Periodic, usually month end, credit or debit | Interest income or interest expense, separately |
| Service Charge | Fixed periodic account management charge | Bank charges expense, own account for visibility |
| Wire Transfer Fee | Only on cross border transfers | Own account, so international cost is visible |
| FX Gain or Loss | Difference caused by a rate, not by a charge | Exchange rate difference accounts |
| Returned Collection Fee | Follows a returned direct debit | Own account, so campaign cost is visible |
| Other | Nothing above fits | Suspense style account, zero auto post ceiling |

Never merge FX into a fee account. They are different economic events, they behave
differently at year end, and merging them makes the fee line useless for negotiation with
the bank.

## Step 3. Check both layers

Run both checks every time. Report which one failed.

### Layer 2, recognition and posting

| Check | Where | Failure symptom |
|---|---|---|
| A bank transaction type exists for this fee | Cash and bank management > Setup > Bank transaction types | Nothing to map to |
| A transaction code mapping row exists on **this** bank account | Cash and bank management > Setup > Transaction code mapping | Line stays unmatched, no error |
| The mapped code equals the code actually in the file | Read `Ntry/BkTxCd/Domn/*` and `Ntry/BkTxCd/Prtry/Cd` from the file | Mapping exists but never fires |
| A Generate voucher rule targets this transaction type | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules | Nothing posts |
| That rule is **activated** | Same page, Activate button | Saved but inert, no warning |
| The rule is in the account's rule set | Reconciliation matching rule sets | Rule exists but never runs |
| Validate transaction type mapping is on or off deliberately | Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation | When on, an unmapped line cannot be matched at all |

### Layer 1, policy

| Check | Where | Failure symptom |
|---|---|---|
| A row exists for this fee type | `templates/fee-and-fx-posting-matrix.csv` | Posts to whatever the rule says, ungoverned |
| The ledger account matches the rule offset account | Compare the matrix to the rule | Posts to the wrong account, silently |
| The amount is within `max_auto_post_amount` | The matrix row | Automated posting of something that should have been approved |
| The account is in scope for this bank account | `applies_to_bank_account` column | A wire fee rule firing on a domestic account |

## Step 4. The two silent failures

Both produce no error message. Both are found only by comparing the layers.

| Failure | Cause | Symptom | Fix |
|---|---|---|---|
| **Policy without mapping** | A row in the posting matrix, no transaction code mapping row | The line stays unmatched forever. Nothing posts. No error | Add the transaction code mapping row on that bank account |
| **Mapping without policy** | A transaction code mapping row, no posting matrix row | It posts, possibly to the wrong account. No warning at all | Add the posting matrix row, and confirm the rule offset account agrees |

The second one is more dangerous. It looks like success.

## Step 5. The gross versus net arithmetic

When the bank supplies the detail:

```
InstdAmt (gross instructed)  -  TtlChrgsAndTaxAmt (charges)  =  Ntry/Amt (net booked)
```

With a currency conversion, before charges:

```
InstdAmt in SrcCcy  *  XchgRate  =  CntrValAmt in TrgtCcy
```

Rules:

1. If `Chrgs/Rcrd/ChrgInclInd` is true, the charge is already inside the booked amount. Do
   not subtract it a second time.
2. If `AmtDtls` and `Chrgs` are absent, the gross and the fee are not in the file. Any
   figure you produce by comparing the booked amount to the open invoice is **derived**.
   Say the word derived.
3. If `XchgRate` is absent, do not back-calculate a rate and present it as the bank's rate.
   Say the bank did not supply it.
4. Never sum fees from a single grid page. The grid returns 25 rows per call. Page the read
   or do not state the total.

## Step 6. FX difference versus fee, on the same payment

A cross border receipt commonly carries both. Split them.

| Component | Amount source | Posts to |
|---|---|---|
| Invoice settlement | Open invoice amount | Customer or vendor account |
| Exchange rate difference | Difference between the invoice rate and the settlement rate | FX gain or FX loss |
| Bank charge | `Chrgs` block, or the residual after the FX difference is accounted for | Bank fee or wire transfer fee |

Realised FX difference on settlement is produced by the settlement itself, using the ledger
exchange rate setup. The reconciliation rule only handles a residual that settlement did not
absorb. When explaining a number, be clear which of the two produced it.

## Step 7. Approval

Before describing anything as automatic, check `max_auto_post_amount` and
`requires_approval_above` in the posting matrix for that fee type and bank account.

- Within the ceiling: automatic posting is appropriate.
- Above the ceiling: the correct answer is that it routes to the named approver role. Say
  that instead of calling it automatic.
- `Other` has a zero ceiling on purpose. Every unclassified line gets a human decision.

## Questions to ask the bank

| Missing | Ask for |
|---|---|
| Net figures only, no breakdown | `AmtDtls/InstdAmt` and a `Chrgs` breakdown per entry |
| No exchange rate on converted amounts | `CcyXchg/XchgRate` with `SrcCcy` and `TrgtCcy` |
| Charges and interest netted into one line | Separate entries, or at least separate `Chrgs/Rcrd` records |
| Statement codes that change without notice | Their format specification and a change notification process |
| No per-item detail inside batch bookings | Detailed booking with `NtryDtls/TxDtls` per item |
