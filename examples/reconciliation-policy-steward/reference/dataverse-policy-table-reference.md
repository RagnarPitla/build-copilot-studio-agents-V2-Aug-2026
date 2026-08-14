# Dataverse policy table reference

Column definitions for the eight `br_` tables, generated from a live environment where
they exist. Use this when reading or maintaining policy, and when explaining to a
customer what needs to be built in their own tenant.

## Status

The tables **do exist** and are shipped with this package.

| Item | Detail |
|---|---|
| Publisher prefix | `br`, chosen so the physical table names match the names used in the agent instructions exactly |
| Solution | `BankReconciliationPolicy`, exported as an unmanaged zip |
| Tables | 8 |
| Seeded demo rows | 25 across 7 tables |

To install them in another environment, import the solution zip that ships alongside
this package, then load the CSV files in `templates/` as the starting policy set.

**One thing that is still missing:** the agent needs a Dataverse tool wired to it before
it can read these tables at runtime. Creating the tables is necessary but not sufficient.
Until that tool exists, say so plainly rather than implying a policy read happened.

## Conventions

| Convention | Value |
|---|---|
| Bank account scope | A single account id, several separated by semicolons, or `ALL` |
| Currency | ISO 4217 three letter code |
| Amounts | Decimal, two places, in the stated currency |
| Dates | ISO 8601 date |
| Timestamps | ISO 8601 UTC with a trailing Z |
| Boolean | Yes or No |
| Boundary rules | Above and including, or Above but excluding. Never leave implicit |

## Relationships

Seven child tables carry a required `br_policyid` lookup back to
`br_reconciliation_policy`. Read the master policy first, then read its children.
`br_reconciliation_log` is standalone by design so an audit entry can never be orphaned
by a policy delete.

## Naming note

`br_reconciliation_log` uses `br_actortype` for the Agent/Human/System choice, not
`br_actor`. A choice column named `br_actor` would auto-generate a virtual label column
called `br_actorname`, which collides with the `br_actorname` text column and breaks the
table's filtered view.

## `br_reconciliation_policy`

Master policy per bank account, confidence thresholds.

Primary name column: `br_policyname`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_bankaccountid` | Text | Yes | Bank Account ID |
| `br_description` | Multiline text | No | Description |
| `br_effectivedate` | Date | Yes | Effective Date |
| `br_expirydate` | Date | No | Expiry Date |
| `br_isactive` | Yes/No | Yes | Is Active |
| `br_isactivename` | Virtual | No |  |
| `br_legalentity` | Text | Yes | Legal Entity |
| `br_matchconfidenceautothreshold` | Whole number | Yes | Match Confidence Auto Threshold |
| `br_matchconfidencesuggestthreshold` | Whole number | Yes | Match Confidence Suggest Threshold |
| `br_policyname` | Text | No | Policy Name |
| `br_reconciliation_policyid` | Unique identifier | Yes | Reconciliation Policy |

## `br_matching_rule`

Named business matching rules and their intent.

Primary name column: `br_rulename`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_confidencethreshold` | Decimal | Yes | Confidence Threshold |
| `br_description` | Multiline text | No | Description |
| `br_isenabled` | Yes/No | Yes | Is Enabled |
| `br_isenabledname` | Virtual | No |  |
| `br_matchcriteria` | Multiline text | Yes | Match Criteria |
| `br_matching_ruleid` | Unique identifier | Yes | Matching Rule |
| `br_matchtype` | Choice | Yes | Match Type |
| | | | Choices: 100000000 = Name Normalization, 100000001 = Reference Extraction, 100000002 = Amount Decomposition, 100000003 = Fee Classification, 100000004 = Date Intelligence, 100000005 = Reversal Detection |
| `br_matchtypename` | Virtual | No |  |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_priority` | Whole number | Yes | Priority |
| `br_rulename` | Text | No | Rule Name |

## `br_tolerance_threshold`

Amount, percentage, date day and FX percentage tolerance.

Primary name column: `br_name`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_description` | Text | No | Description |
| `br_isactive` | Yes/No | Yes | Is Active |
| `br_isactivename` | Virtual | No |  |
| `br_name` | Text | No | Name |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_tolerance_thresholdid` | Unique identifier | Yes | Tolerance Threshold |
| `br_tolerancetype` | Choice | Yes | Tolerance Type |
| | | | Choices: 100000000 = Amount, 100000001 = Percentage, 100000002 = Date Days, 100000003 = FX Percentage |
| `br_tolerancetypename` | Virtual | No |  |
| `br_unit` | Text | Yes | Unit |
| `br_value` | Decimal | Yes | Value |

## `br_auto_posting_rule`

Fee, interest, service charge and FX difference posting.

Primary name column: `br_name`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_auto_posting_ruleid` | Unique identifier | Yes | Auto-Posting Rule |
| `br_description` | Text | No | Description |
| `br_glaccount` | Text | Yes | GL Account |
| `br_isactive` | Yes/No | Yes | Is Active |
| `br_isactivename` | Virtual | No |  |
| `br_journalname` | Text | Yes | Journal Name |
| `br_maxamount` | Currency | Yes | Max Amount |
| `br_name` | Text | No | Name |
| `br_offsetaccount` | Text | Yes | Offset Account |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_requiresapproval` | Yes/No | Yes | Requires Approval |
| `br_requiresapprovalname` | Virtual | No |  |
| `br_transactiontype` | Choice | Yes | Transaction Type |
| | | | Choices: 100000000 = Bank Fee, 100000001 = Interest, 100000002 = Service Charge, 100000003 = Wire Transfer Fee, 100000004 = FX Gain/Loss, 100000005 = Other |
| `br_transactiontypename` | Virtual | No |  |

## `br_approval_chain`

Threshold based approver routing and escalation hours.

Primary name column: `br_name`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_approval_chainid` | Unique identifier | Yes | Approval Chain |
| `br_approveremail` | Text | Yes | Approver Email |
| `br_approverrole` | Text | Yes | Approver Role |
| `br_description` | Text | No | Description |
| `br_escalationhours` | Whole number | Yes | Escalation Hours |
| `br_escalationto` | Text | No | Escalation To |
| `br_name` | Text | No | Name |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_thresholdamount` | Currency | Yes | Threshold Amount |

## `br_exception_rule`

Exception classification, severity and required action.

Primary name column: `br_name`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_action` | Choice | Yes | Action |
| | | | Choices: 100000000 = Auto Clear, 100000001 = Flag for Review, 100000002 = Require Approval, 100000003 = Escalate, 100000004 = Block |
| `br_actionname` | Virtual | No |  |
| `br_condition` | Text | Yes | Condition |
| `br_description` | Multiline text | No | Description |
| `br_exception_ruleid` | Unique identifier | Yes | Exception Rule |
| `br_exceptiontype` | Choice | Yes | Exception Type |
| | | | Choices: 100000000 = Amount Mismatch, 100000001 = No Match, 100000002 = Duplicate Transaction, 100000003 = Stale Item, 100000004 = Suspicious Pattern, 100000005 = FX Variance |
| `br_exceptiontypename` | Virtual | No |  |
| `br_name` | Text | No | Name |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_severity` | Choice | Yes | Severity |
| | | | Choices: 100000000 = Low, 100000001 = Medium, 100000002 = High, 100000003 = Critical |
| `br_severityname` | Virtual | No |  |

## `br_bank_account_config`

Statement format, import frequency, file source.

Primary name column: `br_bankaccountid`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_autoreconcileenabled` | Yes/No | Yes | Auto Reconcile Enabled |
| `br_autoreconcileenabledname` | Virtual | No |  |
| `br_bank_account_configid` | Unique identifier | Yes | Bank Account Config |
| `br_bankaccountid` | Text | No | Bank Account ID |
| `br_filesource` | Text | Yes | File Source |
| `br_importfrequency` | Choice | Yes | Import Frequency |
| | | | Choices: 100000000 = Daily, 100000001 = Weekly, 100000002 = Monthly, 100000003 = On Demand |
| `br_importfrequencyname` | Virtual | No |  |
| `br_lastreconciliationdate` | Date | No | Last Reconciliation Date |
| `br_legalentity` | Text | Yes | Legal Entity |
| `br_policyid` | Lookup | Yes | Policy |
| `br_policyidname` | Text | No |  |
| `br_statementformat` | Choice | Yes | Statement Format |
| | | | Choices: 100000000 = ISO20022 CAMT.053, 100000001 = MT940, 100000002 = BAI2, 100000003 = Custom |
| `br_statementformatname` | Virtual | No |  |

## `br_reconciliation_log`

Immutable audit trail of every action.

Primary name column: `br_name`

| Column | Type | Required | Display name |
| --- | --- | --- | --- |
| `br_action` | Choice | Yes | Action |
| | | | Choices: 100000000 = Statement Imported, 100000001 = Matching Rules Run, 100000002 = Transaction Matched, 100000003 = Transaction Marked New, 100000004 = Journal Created, 100000005 = Journal Posted, 100000006 = Reconciliation Completed, 100000007 = Exception Created, 100000008 = Exception Resolved, 100000009 = Policy Checked, 100000010 = Policy Created, 100000011 = Policy Updated |
| `br_actionname` | Virtual | No |  |
| `br_actorname` | Text | Yes | Actor Name |
| `br_actortype` | Choice | Yes | Actor |
| | | | Choices: 100000000 = Agent, 100000001 = Human, 100000002 = System |
| `br_actortypename` | Virtual | No |  |
| `br_bankaccountid` | Text | Yes | Bank Account ID |
| `br_confidencescore` | Decimal | No | Confidence Score |
| `br_details` | Multiline text | No | Details |
| `br_matchedamount` | Currency | No | Matched Amount |
| `br_name` | Text | No | Name |
| `br_policyapplied` | Text | No | Policy Applied |
| `br_reconciliation_logid` | Unique identifier | Yes | Reconciliation Log |
| `br_statementid` | Text | No | Statement ID |
| `br_timestamp` | Date | Yes | Timestamp |
