# Setup checklist

End-to-end implementation order for Modern bank reconciliation. The order matters. Each
stage depends on the one before it. Skipping ahead produces silent failures rather than
errors.

Mark each item Done, Not applicable, or Blocked, and record who owns it.

## Stage 1. Feature and parameters

| # | Item | Path | Owner |
|---|---|---|---|
| 1.1 | Turn on Modern bank reconciliation | Feature management workspace | System administrator |
| 1.2 | Set number sequences for Download ID, Statement ID, Reconcile ID and Bank reconciliation | Cash and bank management > Setup > Cash and bank management parameters > Number sequences | System administrator |
| 1.3 | Set the Bank statement reversal number sequence, required for Generate voucher | Same page | System administrator |
| 1.4 | Decide Show statement line amount in debit/credit | Cash and bank management > Setup > Cash and bank management parameters > Bank reconciliation | Finance lead |
| 1.5 | Decide Validate transaction type mapping. Turning it on enforces mapping before any match | Same page | Finance lead |
| 1.6 | Set the date difference validation | Same page | Finance lead |
| 1.7 | Decide Require manual matching when advanced bank reconciliation matching rules find multiple documents that match on amount | Same page | Finance lead |

Stage 1.5 and 1.6 override matching rules. Agree them before designing rules, not after.

## Stage 2. Vocabulary

| # | Item | Path | Owner |
|---|---|---|---|
| 2.1 | Create bank transaction types for every kind of line the bank sends | Cash and bank management > Setup > Bank transaction types | Functional consultant |
| 2.2 | At minimum cover deposit, withdrawal, bank fee, interest, service charge, wire transfer fee, FX difference, NSF, reversal | Same page | Functional consultant |
| 2.3 | Agree the ledger account each type will post to | Chart of accounts, and the fee and FX posting matrix in `fee-and-fx-posting-advisor` | Finance lead |

## Stage 3. Format and import

| # | Item | Path | Owner |
|---|---|---|---|
| 3.1 | Import the Advanced bank reconciliation statement model and the ABR ISO20022/camt053 format | Workspaces > Electronic reporting > Microsoft provider > Repositories > Dataverse | System administrator |
| 3.2 | Create the bank statement format record | Cash and bank management > Setup > Advanced bank reconciliation setup > Bank statement format | Functional consultant |
| 3.3 | Select Generic electronic import format and set Import format configuration | Same record | Functional consultant |
| 3.4 | Confirm the source data format time zone | Data management workspace > Configure data sources > Regional settings FastTab | System administrator |
| 3.5 | Obtain a real sample file from the bank and inspect the actual BkTxCd values | The file itself | Functional consultant |

Never design transaction code mapping from the ISO code list alone. Read the customer's own
file. Banks diverge.

## Stage 4. Bank account

Repeat per bank account.

| # | Item | Path | Owner |
|---|---|---|---|
| 4.1 | Advanced bank reconciliation = Yes | Bank account > Reconciliation FastTab | Functional consultant |
| 4.2 | Statement format set to the matching format | Same FastTab | Functional consultant |
| 4.3 | Bank name in statements set, required for multi-account files | Same FastTab | Functional consultant |
| 4.4 | Time zone preference set | Same FastTab | Functional consultant |
| 4.5 | Allowed penny difference agreed and set | Same FastTab | Finance lead |
| 4.6 | Reverse debit credit mark decided | Same FastTab | Functional consultant |
| 4.7 | Clear bridged transactions during reconciliation decided | Same FastTab | Finance lead |
| 4.8 | Customer payment journal and Vendor payment journal set | Same FastTab, Automation | Functional consultant |

## Stage 5. Transaction code mapping

| # | Item | Path | Owner |
|---|---|---|---|
| 5.1 | Create a mapping record for the bank account | Cash and bank management > Setup > Transaction code mapping | Functional consultant |
| 5.2 | Add a mapping row for every distinct statement code seen in the sample file | Same page | Functional consultant |
| 5.3 | Repeat for every bank account. Mapping is per account and does not carry across | Same page | Functional consultant |
| 5.4 | Record the mapping in the editable template shipped with `fee-and-fx-posting-advisor` | `templates/transaction-code-mapping.csv` | Functional consultant |

Mapping done for one account and not another is the most common cause of "it works on
account A but not account B".

## Stage 6. Matching rules

| # | Item | Path | Owner |
|---|---|---|---|
| 6.1 | Create each rule with its action and criteria | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rules | Functional consultant |
| 6.2 | Save each rule | Same page | Functional consultant |
| 6.3 | **Activate** each rule. A saved but inactive rule does nothing and warns nobody | Same page | Functional consultant |
| 6.4 | Create the rule set | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rule sets | Functional consultant |
| 6.5 | Order the rules, most specific first, broadest last | Same page | Functional consultant |
| 6.6 | Set the rule set as Default matching rule set on the bank account | Bank account > Reconciliation FastTab > Automation | Functional consultant |
| 6.7 | Decide Reconcile after import | Same FastTab | Finance lead |

### Rule inventory

Record the rules actually built. Replace these examples with the real ones.

| Rule code | Action | Purpose | Order in set | Active |
|---|---|---|---|---|
| R10-REVSTMT | Clear reversal statement lines | Remove bank error reversals before anything else sees them | 1 | Yes |
| R20-REVCOMP | Clear reversal company transaction | Clear our own reversed payment journals | 2 | Yes |
| R30-FEE | Generate voucher | Post bank charge lines to the bank fee account | 3 | Yes |
| R40-INT | Generate voucher | Post interest lines to the interest account | 4 | Yes |
| R50-CUSTSETTLE | Settle customer invoice | Settle open customer and donation invoices, exact reference | 5 | Yes |
| R60-CUSTPAY | Generate customer payment | Post incoming payments with no matched invoice | 6 | Yes |
| R70-VENDPAY | Generate vendor payment | Post outgoing vendor payments | 7 | Yes |
| R80-DOCMATCH | Match with bank document | Broad catch-all match on amount and date tolerance | 8 | Yes |

## Stage 7. Test

| # | Item | Evidence |
|---|---|---|
| 7.1 | Import a real bank file into a test environment | Data management job history shows success |
| 7.2 | Confirm every statement line received a bank transaction type | No unmapped codes on the worksheet |
| 7.3 | Confirm opening plus net booked equals closing balance | Statement balances |
| 7.4 | Run the rule set. Record the match rate | Worksheet Matched and Unmatched tabs |
| 7.5 | Review every unmatched line and classify it | Use `match-exception-explainer` |
| 7.6 | Confirm fee and FX lines posted to the intended accounts | Voucher transactions |
| 7.7 | Reverse one generated voucher to prove the reversal path works | Worksheet Matched transactions > Reverse |
| 7.8 | Record job duration before and after any change | Data management job history |

## Stage 8. Go live and after

| # | Item |
|---|---|
| 8.1 | Agree who reviews unmatched lines daily and by when |
| 8.2 | Agree the tolerance review cadence. Tolerances set once and never revisited go stale |
| 8.3 | Agree the escalation path when the bank changes its format without notice |
| 8.4 | Record the residual manual work honestly, so nobody is surprised in month one |
