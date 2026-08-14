# Dashboard layout

The presentation template. Edit this file to change what the dashboard shows and how it
reads. The instructions reference this layout rather than hardcoding it, so changes here take
effect without touching SKILL.md.

Everything below renders as normal message text. Adaptive cards cannot carry live data, so
they are not an option here.

## Block order

| # | Block | Always shown | Purpose |
|---|---|---|---|
| 1 | Statement | Yes | Identity and balances |
| 2 | Position | Yes | Matched versus unmatched |
| 3 | Needs attention | Only when there is something | Grouped exceptions |
| 4 | Money movement | Optional | Fees, FX and adjustments |
| 5 | Detail | On request, or when the line count is small | Line level table |
| 6 | Next | Yes | What a person does |

Drop any block with nothing to say. An empty block is noise.

## Block 1. Statement

```
Statement STM-2026-0034
Account BANK-EUR-02 EUR   Period 2026-02-04
Opening 412,880.15   Closing 431,004.72   Source header balances
```

Rules:

- Take opening and closing from the statement header balances, `OPBD` and `CLBD`. They are
  authoritative and cost one read.
- Never compute a closing balance by summing lines.
- If opening plus net booked does not equal closing, say so here. It means the file is
  incomplete or lines were filtered. That is the most important thing on the whole dashboard.

## Block 2. Position

```
Position
  Lines           412
  Matched         371   18,004.11 EUR
  Unmatched        41      120.61 EUR
  Coverage        read 17 of 17 pages
```

Rules:

- Always show coverage. A number without coverage is not usable.
- If paging is incomplete, write the coverage as read 4 of 17 pages and label the figures
  partial.
- Group by currency where an account carries more than one. Never sum across currencies.

## Block 3. Needs attention

```
Needs attention
  MX-03  Transaction code not mapped        28    41.20 EUR   Configuration, fix once
  MX-09  Reference missing or unusable       9    62.41 EUR   Line by line
  MX-18  Batch entry with no item detail     1    16.00 EUR   Bank request
  MX-16  Multiple candidates on amount       3     1.00 EUR   Needs a person
```

Rules:

- Group by reason code from `match-exception-explainer`. Never present a flat list of lines.
- Order by severity first, then by count.
- The last column says what kind of action it is: fix once, line by line, bank request, or
  needs a person. This is what turns a report into something actionable.
- One configuration fix usually clears a whole group. Say which group that is.

## Block 4. Money movement

```
Money movement
  Bank fees            14 lines      112.40 EUR   posted 610100
  Interest              1 line         3.02 EUR   posted 810100
  FX differences        0 lines
  Awaiting approval     2 lines      680.00 EUR   Treasury Accountant
```

Rules:

- Only show what was actually read from posted vouchers. Never show what should have posted.
- Show the ledger account, so an incorrect mapping is visible immediately.
- Show lines awaiting approval with the approver role, taken from the approval chain.
- Omit the whole block if nothing moved.

## Block 5. Detail

A markdown table using the default field set from `transaction-line-fields.csv`.

```
| Date | Payer | Gross | Fees | Net | Currency | Reference | Type | Status |
|---|---|---|---|---|---|---|---|---|
| 2026-02-04 | Muster GmbH | 1,250.00 | 3.50 | 1,246.50 | EUR | INV-4417 | DEP | Matched |
| 2026-02-04 | A. Schneider | 50.00 |  | 50.00 | EUR | DON-2026-Q1 | DEP | Matched |
| 2026-02-04 | Bank charge |  | 12.40 | -12.40 | EUR |  | FEE | Posted 610100 |
| 2026-02-04 | Collection batch |  |  | 8,420.00 | EUR | 412 items | DEP | Batch no detail |
```

Rules:

- Gross, fees and net on the same row. This is the single most important presentation
  decision in the whole solution and the thing the current state does worst.
- A blank cell means the bank did not supply the value. Leave it blank. Never fill it.
- Where a value is derived rather than reported, mark it with the word derived in the row, or
  add a footnote under the table.
- Cap at 25 rows in one message. Beyond that, summarise and offer the next page.
- Sort by booking date, then by amount descending.

## Block 6. Next

```
Next
  1. Add transaction code mapping for code 808 on BANK-EUR-02
     Cash and bank management > Setup > Transaction code mapping
     Clears 28 lines. Owner functional consultant.
  2. Approve 2 lines above the auto post ceiling
     Cash and bank management > Bank statement reconciliation > Bank reconciliation
     Owner Treasury Accountant.
  3. Ask the bank for per item detail on batch bookings
     Owner treasury.
```

Rules:

- Maximum three actions. More than three and nobody does any of them.
- Each action names the exact navigation path, the effect and the owner.
- Put the fix-once configuration action first. It has the highest leverage.

## Style

| Rule | Reason |
|---|---|
| Numbers right aligned in fixed blocks, thousands separated | Scanability |
| Currency stated once per block, not on every number | Less noise |
| Dates as ISO, YYYY-MM-DD | Unambiguous across DACH and international readers |
| No colour, no emoji, no icons | They do not survive copying into an email or a ticket |
| Coverage stated wherever a figure came from paging | Honesty about partial reads |
| Blank rather than zero when a value is absent | Zero and unknown are different facts |

## Variants

Set these by editing the block table at the top.

| Variant | Blocks | Use |
|---|---|---|
| Daily check | 1, 2, 3, 6 | Every morning. Under 20 lines of output |
| Post import | 1, 2, 5, 6 | Immediately after upload, when line visibility is the point |
| Period close | 1, 2, 3, 4, 6 | Month end, with money movement and approvals |
| Single line | 5 only | One line, full field set, nothing else |
