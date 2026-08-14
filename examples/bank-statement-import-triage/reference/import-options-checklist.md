# Import options checklist

Work through this in order. Most reported slowness is one of checks 1 to 4. Record what you
find, then split it into what configuration fixes and what is a constraint.

Navigation paths are for Dynamics 365 Finance with the Modern bank reconciliation feature
turned on in the Feature management workspace.

## 1. Is a person waiting on the import

| Check | Where | What good looks like |
|---|---|---|
| Which route is used to import | Ask the user | Recurring Data management job or Power Automate, not the interactive dialog |
| Is the job running in batch | Data management workspace > the import project > Run in batch | Batch enabled, so nobody is held at the screen |
| Is there a batch group with capacity | System administration > Setup > Batch group | A dedicated group, not competing with the nightly close jobs |

If the answer is the interactive Import statement dialog, that alone explains "the user
waits". Fixing this does not make the import faster. It stops a person having to watch it.
Say both halves of that sentence.

## 2. Is the statement being reconciled after import

| Check | Where | What good looks like |
|---|---|---|
| Reconcile after import | Cash and bank management > Bank accounts > Bank accounts > Reconciliation FastTab > Automation | Yes |
| Default matching rule set | Same FastTab | A populated, activated rule set |
| Rules inside the set are ordered | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rule sets | Most specific rules first, broadest last |
| Every rule is activated | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules | Activate has been selected on each rule |

A rule that is saved but not activated does nothing. This is the single most common cause of
"the import worked but nothing matched".

## 3. Is the file the right size and cadence

| Check | Where | What good looks like |
|---|---|---|
| Delivery frequency | Bank agreement, recorded in the import profile template | Daily at minimum. Intraday for high-volume donation accounts |
| Lines per file | Count from the statement, paged | Consistent and predictable |
| One file per account or multi-account file | Inspect the file | Either is fine, but multi-account requires check 4 |
| Batch booking in use | `Ntry/NtryDtls/Btch/NbOfTxs` in the file | Detail present per transaction, see the CAMT.053 field reference |

Reducing file size is the only lever that reliably reduces the work in one import job. It
comes from the bank, not from D365.

## 4. Is the account configuration correct

| Field | Where | Note |
|---|---|---|
| Advanced bank reconciliation | Bank account > Reconciliation FastTab | Must be Yes |
| Statement format | Same FastTab | Must match the actual file format. A mismatch fails the import |
| Bank name in statements | Same FastTab | Required when one file contains several accounts |
| Time zone preference | Same FastTab | Set to the local time zone of the date and time values in the file |
| Reverse debit credit mark | Same FastTab | Only when the bank reports from its own perspective |
| Allowed penny difference | Same FastTab | Sets the maximum amount variance tolerated on a match |
| Clear bridged transactions during reconciliation | Same FastTab | Decide deliberately, do not leave to chance |

## 5. Is the format configuration correct

| Check | Where |
|---|---|
| Electronic reporting configuration imported | Workspaces > Electronic reporting > Microsoft provider > Repositories > Dataverse. Look for the Advanced bank reconciliation statement model, then the ABR ISO20022/camt053 format |
| Bank statement format record exists | Cash and bank management > Setup > Advanced bank reconciliation setup > Bank statement format |
| Generic electronic import format checkbox | On the bank statement format record. Must be selected when using an Electronic reporting configuration |
| Import format configuration | On the same record, pointing at the imported ER format |
| Source data format time zone | Data management workspace > Configure data sources > select the format > Regional settings FastTab |

The legacy Data management transformation route using XSLT files still exists but was
deprecated in September 2022. New setups should use Electronic reporting.

## 6. Is the import actually failing rather than being slow

| Check | Where |
|---|---|
| Job status and duration | Data management workspace > Job history |
| The real error | Job history > Execution details > View execution log |
| Duplicate statement | Compare statement `Id`, `ElctrncSeqNb` and `AcctSvcrRef` against already imported statements |
| Balance continuity | Opening balance plus net booked entries equals closing balance |

Read the execution log before offering a theory. A transformation error means the bank has
diverged from the standard format, which is an Electronic reporting configuration problem,
not a matching problem.

## 7. Parameters that override everything else

Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation.

| Parameter | Effect |
|---|---|
| Validate transaction type mapping | When on, transaction types must be mapped before a line can be matched, manually or automatically |
| Date difference validation | Caps how far apart dates can be. This overrides the matching rules |
| Require manual matching when advanced bank reconciliation matching rules find multiple documents that match on amount | Forces a human decision instead of taking the first match |
| Show statement line amount in debit/credit | Splits amounts into debit and credit columns on the Bank statement page |

The validation options on this page override the selections on matching rules. If a rule
appears to be ignored, check here before changing the rule.

Number sequences on the same page must be set for Download ID, Statement ID, Reconcile ID
and Bank reconciliation. Voucher generation additionally needs the Bank statement reversal
reference number sequence.

## 8. Measure it

Record before and after from Data management job history:

- job start time and end time
- number of records processed
- whether the job ran in batch and in which batch group

Do not quote an expected improvement. Report the measured one.

## Escalate to the bank, not to IT

| Symptom | Ask the bank for |
|---|---|
| One monthly file only | Daily or intraday delivery |
| Batch-booked entries with no per-transaction detail | Detailed booking, with `NtryDtls/TxDtls` per item |
| Fees visible only as a net figure | `AmtDtls/InstdAmt` and a `Chrgs` breakdown |
| Truncated remittance text | Full `RmtInf/Ustrd` |
| No exchange rate on converted amounts | `CcyXchg/XchgRate` |
| Unstable references between files | A stable `AcctSvcrRef` |
