# BankReconciliationPolicy solution

`BankReconciliationPolicy_1_0_0_0.zip` is an unmanaged Dataverse solution containing the
eight `br_` policy tables.

## What is in it

| Table | Governs |
| --- | --- |
| `br_reconciliation_policy` | Master policy per bank account, confidence thresholds |
| `br_matching_rule` | Named business matching rules and their intent |
| `br_tolerance_threshold` | Amount, percentage, date day and FX percentage tolerance |
| `br_auto_posting_rule` | Fee, interest, service charge and FX difference posting |
| `br_approval_chain` | Threshold based approver routing and escalation hours |
| `br_exception_rule` | Exception classification, severity and required action |
| `br_bank_account_config` | Statement format, import frequency, file source |
| `br_reconciliation_log` | Immutable audit trail of every action |

Publisher prefix is `br`, chosen deliberately so the physical table names match the names
already used in the agent instructions. No instruction rewrite is needed after import.

## To install

1. Power Apps maker portal, choose the target environment.
2. Solutions, Import solution, browse to this zip.
3. Import. The publisher `bankreconpublisher` is created if it is not already present.
4. Load the CSV files in `../templates/` as the starting policy set. Their headers match
   the real column names, so they import without remapping.

## After import

The tables alone are not enough. The agent also needs a **Dataverse tool** connected to it
before it can read policy at runtime. Without that tool, this skill stays in Mode B and must
say so rather than implying a live read.
