# D365 navigation paths

Dynamics 365 Finance, Modern bank reconciliation. Paths verified against current Microsoft
documentation. If a path has been renamed by a version upgrade, correct it here rather than
in the instructions.

Give the full path every time. Never say "in the reconciliation settings".

## Feature enablement

| What | Path |
|---|---|
| Modern bank reconciliation feature | Feature management workspace, search for Modern bank reconciliation, then Enable now |
| Offset account financial dimensions on reconciliation vouchers | Feature management workspace, Enable offset account financial dimensions for general ledger voucher posting during bank account reconciliation |

Modern bank reconciliation objects and code are subject to change. Microsoft states the
related classes, forms and tables should not be customised. Treat customisation of the
reconciliation worksheet forms as out of scope.

## Core setup

| What | Path |
|---|---|
| Bank transaction types | Cash and bank management > Setup > Bank transaction types |
| Transaction code mapping, per bank account | Cash and bank management > Setup > Transaction code mapping |
| Bank statement format | Cash and bank management > Setup > Advanced bank reconciliation setup > Bank statement format |
| Reconciliation matching rules | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules |
| Reconciliation matching rule sets | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rule sets |
| Cash and bank management parameters | Cash and bank management > Setup > Cash and bank management parameters |
| Bank reconciliation parameters | Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation |
| Number sequences for reconciliation | Cash and bank management > Setup > Cash and bank management parameters > Number sequences |

## Bank account

| What | Path |
|---|---|
| Bank accounts list | Cash and bank management > Bank accounts > Bank accounts |
| Reconciliation settings for an account | Cash and bank management > Bank accounts > Bank accounts > open the account > Reconciliation FastTab |
| Bank statements for an account | Cash and bank management > Bank accounts > Bank accounts > open the account > Reconcile tab > Bank statements |
| Import a statement interactively | Bank statement page > Import statement |

### Reconciliation FastTab, general settings

| Field | Effect |
|---|---|
| Advanced bank reconciliation | Enables modern bank reconciliation for this account. Unlocks electronic import, automatic matching and the rest of the tab |
| Use bank statements as confirmation of electronic payment | Creates a bank document when a payment is set to Sent, and updates it from Sent to Received once matched, reconciled and posted |
| Allowed penny difference | Maximum amount variance tolerated when matching. 0.00 means amounts must match exactly |
| Statement format | The import format or ER configuration used to parse this account's files |
| Bank name in statements | The identifier the bank uses for this account. Required to pick the right account out of a multi-account file |
| Time zone preference | Time zone applied when interpreting statement timestamps. Auto uses the system or user default |
| Reverse debit credit mark | Flips the sign of imported amounts when the bank reports from its own perspective |
| Clear bridged transactions during reconciliation | When Yes, bridged or pending entries are cleared during reconciliation rather than separately |

### Reconciliation FastTab, automation

| Field | Effect |
|---|---|
| Reconcile after import | Validates the statement, creates a reconciliation and worksheet, and runs the default matching rule set as soon as a statement is imported |
| Default matching rule set | The rule set applied during reconciliation, and the one used by Reconcile after import |
| Customer payment journal | Default journal for customer payments generated during reconciliation |
| Vendor payment journal | Default journal for vendor payments generated during reconciliation |
| Default report configuration | ER configuration used for the reconciliation report format and layout |

## Reconciliation worksheet

| What | Path |
|---|---|
| Bank reconciliation worksheet | Cash and bank management > Bank statement reconciliation > Bank reconciliation |
| Run a rule set or a single rule on demand | Bank reconciliation worksheet > Run matching rules |
| Post non-payment lines to the general ledger | Bank reconciliation worksheet > Unmatched transactions tab > select lines > Generate voucher |
| Reverse a posted reconciliation voucher | Bank reconciliation worksheet > Matched transactions tab > select lines > Reverse |

Worksheet tabs: Unmatched transactions, Matched transactions.

## Electronic reporting for statement import

| What | Path |
|---|---|
| Electronic reporting workspace | Workspaces > Electronic reporting |
| Import an ABR format configuration | Workspaces > Electronic reporting > Microsoft configuration provider tile > Repositories > Dataverse > Open |
| The model to look for | Advanced bank reconciliation statement model |
| The CAMT.053 format | ABR ISO20022/camt053 format |
| The MT940 format | ABR MT940 format |
| The BAI2 format | ABR BAI2 format |

On the bank statement format record, select the Generic electronic import format checkbox
and set Import format configuration to the imported ER format. The statement format chosen
on the bank account must match the actual file format or the import fails.

The older Data management transformation route using XSLT resource files was deprecated in
September 2022. Use Electronic reporting for new setups.

## Data management

| What | Path |
|---|---|
| Data management workspace | Workspaces > Data management |
| Source data format and time zone | Data management workspace > Configure data sources > select the format > Regional settings FastTab > Time zone preference |
| Job history | Data management workspace > Job history |
| The real import error | Job history > Execution details > View execution log |

## Bank reconciliation parameters that override matching rules

Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation.

| Parameter | Effect |
|---|---|
| Validate transaction type mapping | Transaction types must be mapped before a line can be matched, manually or automatically |
| Date difference validation | Caps the date gap allowed on a match. Overrides the matching rules |
| Require manual matching when advanced bank reconciliation matching rules find multiple documents that match on amount | Forces a human decision rather than taking the first match |
| Show statement line amount in debit/credit | Splits statement amounts into separate debit and credit columns |

The validation options on this page override the selections on matching rules.

## Number sequences required

Cash and bank management > Setup > Cash and bank management parameters > Number sequences.

| Reference | Needed for |
|---|---|
| Download ID | Statement download |
| Statement ID | Statement import |
| Reconcile ID | Reconciliation |
| Bank reconciliation | Reconciliation |
| Bank statement reversal | Generate voucher and reversal handling |
