# Requirement to config map

The decision table. Look the requirement up here before reasoning from first principles.

Verdict values:

- **Native config** - the product does this. It needs setting up, not building.
- **Native config plus constraint** - configuration helps, and something real remains.
- **Genuine gap** - configuration does not close this. An agent adds value here.

## The seven requirements

| # | Requirement | Verdict | Native mechanism | Where |
|---|---|---|---|---|
| 1 | Large statement handling, reduced upload time, background processing so the workflow is not blocked | Native config plus constraint | Batch import, Reconcile after import, smaller and more frequent files | Bank account Reconciliation FastTab, Data management batch job, bank agreement |
| 2 | Scalability at high transaction volumes, parallel or incremental loading | Native config plus constraint | More frequent smaller files, incremental daily import. There is no parallel import of a single file | Bank agreement, Data management recurring job |
| 3 | Flexible matching when payment does not equal invoice due to fees or FX, split posting, automatic allocation of differences | Native config | Matching rules with tolerances, Generate voucher, offset account, Allowed penny difference | Reconciliation matching rules, bank account Reconciliation FastTab |
| 4 | Automatic detection and calculation of bank charges and FX differences | Native config | Bank transaction types plus transaction code mapping, Generate voucher rule with fee and FX offset accounts | Bank transaction types, Transaction code mapping, Reconciliation matching rules |
| 5 | Partial and complex matching, one to many and many to one, residual postings, audit trail of split allocations | Native config | Matching rule matching type, tolerances, residual to offset account, voucher and reversal audit trail | Reconciliation matching rules and rule sets |
| 6 | Transaction-level detail visible immediately after upload, showing fees, gross versus net, payment references | **Genuine gap** | Partial only. Data exists in the statement and in D365 but requires drill-down across screens to assemble | Hand to `reconciliation-dashboard-reporter` |
| 7 | Reconciliation dashboard with all booking detail inline, avoiding drilling into multiple screens | **Genuine gap** | Not native as a single consolidated view | Hand to `reconciliation-dashboard-reporter` |

## Common phrasings and what they actually are

| The user says | It is really | Verdict | Do this |
|---|---|---|---|
| The payment is short because the bank took a fee | Residual allocation | Native config | Generate voucher rule for the fee line, or offset account on the settlement rule |
| We receive less than the invoice because of the exchange rate | FX difference recognition | Native config | FX difference offset account, driven by bank transaction type mapping |
| One transfer pays six invoices | One to many matching | Native config | Matching rule with the appropriate matching type and tolerances |
| Six small transfers pay one invoice | Many to one matching | Native config | Same, in the other direction |
| We need to split a payment across accounts during reconciliation | Split posting with residual allocation | Native config | Settlement rule for the invoice portion, offset account for the remainder |
| It matched the wrong invoice | Rule ordering, or first-match behaviour | Native config | Reorder the rule set. Turn on Require manual matching when multiple documents match on amount |
| Nothing matches at all | Rule not activated, or transaction code mapping missing for the account | Native config | Activate the rule. Check the mapping on that specific account |
| Bank interest and account fees have to be keyed manually every month | Non-payment lines to the general ledger | Native config | Generate voucher rule, with bank transaction type and offset account |
| Reversals from a bank error clutter the worksheet | Reversal clearing | Native config | Clear reversal statement lines rule |
| Our own reversed payment journals never clear | Company reversal clearing | Native config | Clear reversal company transaction rule |
| We want approval before a difference is posted | Governance | Policy, not native reconciliation | Hand to `reconciliation-policy-steward`, and use approval workflow on the journal |
| We cannot see what is inside a statement line | Detail visibility | **Genuine gap** | Hand to `reconciliation-dashboard-reporter` |
| We want one screen like BMD | Consolidated presentation | **Genuine gap** | Hand to `reconciliation-dashboard-reporter` |
| It takes forever to upload | Import performance | Native config plus constraint | Hand to `bank-statement-import-triage`. Never quote a speed figure |
| Why did this specific line not match | Exception explanation | Explanation, not config | Hand to `match-exception-explainer` |

## What is not native and should not be promised

| Ask | Reality |
|---|---|
| Parallel import of one statement file | Not available. Split delivery instead |
| A guaranteed import duration | Cannot be substantiated. Never state one |
| Per-donor detail inside a batch-booked entry where the bank sent no per-item detail | The data is not in the file. Only the bank can fix it |
| Live data rendered inside an adaptive card | Adaptive cards in Copilot Studio are static JSON with no Power Fx interpolation in the card body. Use normal message output |
| The agent uploading a statement file | MCP has no file upload. Use Power Automate plus Electronic reporting |
| The agent performing the match itself | Prohibited. Run the native rule set and report the result |

## Version notes

| Item | Note |
|---|---|
| Modern bank reconciliation | Available from 10.0.41. Below that version the Modern-only rule actions do not exist |
| Generate voucher, Generate customer payment, Generate vendor payment, Settle customer invoice, Clear reversal company transaction | Modern actions. Require the feature to be on |
| Mark new transactions | Base action, not available when Modern is on |
| Bulk approve and reject | Private preview at 10.0.46. Do not present as generally available |
| Legacy XSLT statement import | Deprecated September 2022. Use Electronic reporting |
