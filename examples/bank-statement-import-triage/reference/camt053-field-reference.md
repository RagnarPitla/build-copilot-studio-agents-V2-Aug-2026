# CAMT.053 field reference

ISO 20022 `camt.053.001.xx` bank-to-customer statement. Element paths are given relative to
`Document/BkToCstmrStmt/Stmt`.

Use this file to decide which fields you need from the bank, to check whether a field the
business is asking for actually exists in the file, and to write the field list for the
dashboard skill.

Not every bank sends every element. Optional elements that are absent cannot be recovered
by configuration. They have to be requested from the bank.

## Statement header

| Element path | Meaning | Why it matters |
|---|---|---|
| `Id` | Statement identifier | Detects duplicate imports |
| `ElctrncSeqNb` | Electronic sequence number | Detects a missing statement in the sequence |
| `LglSeqNb` | Legal sequence number | Same, on the legal numbering |
| `CreDtTm` | File creation timestamp | Time zone interpretation, see the import checklist |
| `FrToDt/FrDtTm` and `FrToDt/ToDtTm` | Period covered | Confirms the file covers the expected days |
| `Acct/Id/IBAN` | Account IBAN | Selects the right D365 bank account |
| `Acct/Ccy` | Account currency | Base currency of the statement |
| `Acct/Ownr/Nm` | Account owner name | Sanity check on the right legal entity |
| `Acct/Svcr/FinInstnId/BICFI` | Servicing bank BIC | Identifies the bank |

## Balances

| Element path | Meaning |
|---|---|
| `Bal/Tp/CdOrPrtry/Cd` | Balance type code. `OPBD` opening booked, `CLBD` closing booked, `CLAV` closing available, `PRCD` previously closed booked, `FWAV` forward available |
| `Bal/Amt` and its `Ccy` attribute | Balance amount and currency |
| `Bal/CdtDbtInd` | `CRDT` or `DBIT`. A debit-indicated balance is negative in ledger terms |
| `Bal/Dt/Dt` | Balance date |

Opening balance plus the net of booked entries should equal the closing balance. If it does
not, the file is incomplete or entries have been filtered. Report that rather than
reconciling around it.

## Entry level, one per booked line

| Element path | Meaning | Why it matters |
|---|---|---|
| `Ntry/NtryRef` | Bank entry reference | Optional, useful as a match key when present |
| `Ntry/Amt` and `Ccy` attribute | **Booked amount, net of deducted charges** | This is the amount that actually moved. It is the net figure |
| `Ntry/CdtDbtInd` | `CRDT` or `DBIT` | Direction |
| `Ntry/RvslInd` | Reversal indicator | Drives the Clear reversal statement lines matching rule action |
| `Ntry/Sts` or `Ntry/Sts/Cd` | `BOOK`, `PDNG`, `INFO` | Only `BOOK` is a real booking. Pending lines must not be reconciled |
| `Ntry/BookgDt/Dt` | Booking date | Primary date for date tolerance |
| `Ntry/ValDt/Dt` | Value date | Often differs from booking date. Choose one deliberately and be consistent |
| `Ntry/AcctSvcrRef` | Account servicer reference | Bank's own unique reference, often the best duplicate key |
| `Ntry/BkTxCd/Domn/Cd` | Domain code, for example `PMNT` | First part of the bank transaction code |
| `Ntry/BkTxCd/Domn/Fmly/Cd` | Family code | Second part |
| `Ntry/BkTxCd/Domn/Fmly/SubFmlyCd` | Sub-family code | Third part |
| `Ntry/BkTxCd/Prtry/Cd` | Proprietary bank code | The bank's own code. In DACH this is commonly the business transaction code used by the bank |
| `Ntry/BkTxCd/Prtry/Issr` | Issuer of the proprietary code | Tells you whose code scheme it is |
| `Ntry/AddtlNtryInf` | Free text on the entry | Often the only place a fee is described |

**The `BkTxCd` elements are the input to D365 transaction code mapping.** Whatever value
you map in Cash and bank management > Setup > Transaction code mapping must be the value
that actually appears in these elements in your own file. Read the file, do not assume.

## Gross versus net, and charges

This is the group that answers requirement 6 and most of requirement 4.

| Element path | Meaning |
|---|---|
| `Ntry/AmtDtls/InstdAmt/Amt` | **Instructed amount, the gross amount the payer instructed** |
| `Ntry/AmtDtls/TxAmt/Amt` | Transaction amount as processed |
| `Ntry/AmtDtls/CntrValAmt/Amt` | Counter value amount after currency conversion |
| `Ntry/AmtDtls/CntrValAmt/CcyXchg/SrcCcy` | Source currency |
| `Ntry/AmtDtls/CntrValAmt/CcyXchg/TrgtCcy` | Target currency |
| `Ntry/AmtDtls/CntrValAmt/CcyXchg/XchgRate` | **Exchange rate applied by the bank** |
| `Ntry/Chrgs/TtlChrgsAndTaxAmt` | Total charges and taxes on the entry |
| `Ntry/Chrgs/Rcrd/Amt` | Individual charge amount |
| `Ntry/Chrgs/Rcrd/CdtDbtInd` | Whether the charge was debited or credited |
| `Ntry/Chrgs/Rcrd/ChrgInclInd` | Whether the charge is already included in the entry amount |
| `Ntry/Chrgs/Rcrd/Tp/Prtry/Id` | Charge type identifier |
| `Ntry/Chrgs/Rcrd/Br` | Bearer of the charge, for example `DEBT`, `CRED`, `SHAR` |

The arithmetic that explains a short payment:

```
InstdAmt (gross)  -  TtlChrgsAndTaxAmt (fees)  =  Ntry/Amt (net booked)
```

and where currency conversion is involved:

```
InstdAmt in SrcCcy  *  XchgRate  =  CntrValAmt in TrgtCcy, before charges
```

If `ChrgInclInd` is true, the charge is already inside the booked amount and must not be
subtracted a second time. Getting this wrong is the most common cause of a
double-counted fee.

If the bank does not populate `AmtDtls` or `Chrgs`, the gross amount and the fee are not in
the file. The difference can still be derived by comparing the booked amount to the open
invoice amount in D365, but the fee breakdown itself is unavailable and must be requested
from the bank. Say that rather than presenting a derived figure as a bank-reported figure.

## Transaction detail level, inside an entry

Path prefix `Ntry/NtryDtls/TxDtls`.

| Element path | Meaning |
|---|---|
| `Refs/EndToEndId` | **End to end reference set by the payer. Usually the strongest match key** |
| `Refs/MsgId` | Message identifier |
| `Refs/InstrId` | Instruction identifier |
| `Refs/TxId` | Transaction identifier |
| `Refs/MndtId` | Mandate identifier for direct debits |
| `Refs/AcctSvcrRef` | Bank reference at transaction level |
| `Amt` and `CdtDbtInd` | Amount and direction of this individual transaction |
| `AmtDtls/...` | Same gross, transaction and counter value structure as at entry level |
| `Chrgs/...` | Same charge structure as at entry level |
| `RltdPties/Dbtr/Nm` | **Payer name. For a nonprofit this is the donor name** |
| `RltdPties/DbtrAcct/Id/IBAN` | Payer IBAN |
| `RltdPties/UltmtDbtr/Nm` | Ultimate payer, when a payment is routed through an intermediary |
| `RltdPties/Cdtr/Nm` | Payee name |
| `RltdPties/CdtrAcct/Id/IBAN` | Payee IBAN |
| `RltdAgts/DbtrAgt/FinInstnId/BICFI` | Payer bank BIC |
| `RmtInf/Ustrd` | **Unstructured remittance text. Where invoice numbers and donation references usually live** |
| `RmtInf/Strd/CdtrRefInf/Ref` | Structured creditor reference, for example an RF reference |
| `AddtlTxInf` | Free text at transaction level |

## Batch booking

| Element path | Meaning |
|---|---|
| `Ntry/NtryDtls/Btch/MsgId` | Batch message identifier |
| `Ntry/NtryDtls/Btch/PmtInfId` | Payment information identifier |
| `Ntry/NtryDtls/Btch/NbOfTxs` | **Number of transactions collapsed into this one entry** |
| `Ntry/NtryDtls/Btch/TtlAmt` | Total amount of the batch |

This is the single most important thing to check for a high-volume donation account.

- If `NbOfTxs` is greater than 1 and there is a matching `TxDtls` element per transaction,
  the detail exists and per-donor visibility is achievable.
- If `NbOfTxs` is greater than 1 and there is only one summarised `TxDtls`, or none, the
  detail does not exist in the file. Per-donor visibility is impossible from this file at
  any price. The bank must be asked to send detailed booking, or a separate collection
  file must be sourced.

Check this before promising anything about transaction-level visibility.

## Fields most often missing in practice

Ask the bank for these explicitly when the business needs them.

1. `AmtDtls/InstdAmt` on entries where a fee was deducted
2. `Chrgs` breakdown rather than a net figure only
3. Per-transaction `TxDtls` inside batch-booked entries
4. `RmtInf/Ustrd` preserved in full rather than truncated
5. `CcyXchg/XchgRate` on converted amounts
6. A stable `AcctSvcrRef` for duplicate detection
