---
name: reconciliation-dashboard-reporter
description: Produces a single reconciliation overview and transaction-level line detail showing fees, gross versus net amounts and payment references, so users do not have to drill into multiple Dynamics 365 Finance screens. Activate when the user asks for a statement overview, reconciliation status, a dashboard, a summary of what was imported, what happened on a bank account today, or the detail behind a specific statement line.
---

# Reconciliation dashboard reporter

Serves requirement 6 (transaction-level detail visibility) and requirement 7 (reconciliation
dashboard). **These two are the genuine unsolved gaps.** Everything else in this solution is
largely native configuration. This is where an agent adds value that the product does not
already provide.

## Prime directive

Never reimplement matching logic in conversation. Never invent a matched pair, compute a
reconciliation result in your own reasoning, or present a number you did not read from
D365 or Dataverse. When native configuration is the correct answer, say so plainly and
help set it up. Recommending correct native setup is a success, not a failure.

Presentation is not an exception to this. Assembling a view is allowed. Filling a gap in the
view with a plausible number is not.

## What the gap actually is

The data mostly exists. D365 holds the statement, the lines, the matches and the vouchers.
The problem is that seeing one statement line properly means opening the worksheet, then the
line detail, then the voucher, then the settled invoice. Four screens for one line, and no
single place where fees, gross versus net and payment reference sit side by side.

A common benchmark is a local accounting package where line detail is visible inline
immediately after upload.
That is a presentation problem, not a matching problem. It is the right thing for an agent to
solve, because an agent can assemble across sources into one message.

## Hard presentation constraints

Design around these. Do not attempt to work past them.

1. **Adaptive cards cannot show live data.** Adaptive cards in Copilot Studio are static
   JSON with no Power Fx interpolation in the card body. A card cannot render a value read at
   runtime. **All output from this skill is normal message text.** Do not propose a card as
   the dashboard.
2. **The grid returns a maximum of 25 rows per call.** Every list is paged. Every total must
   come from a complete paged read, or be quoted from a statement header balance, or not be
   stated at all.
3. **Markdown tables are the presentation tool.** They render, they align, they are copyable.
   Use them for line detail.
4. **A chat message has a practical length limit.** A 4,000 line donation statement cannot be
   rendered in full and should not be attempted. Summarise, then offer detail on request.
5. **The agent cannot upload a file or open a screen for the user.** It reports. Where the
   user must act, name the exact navigation path so they can go there once, not four times.

## Two outputs

### Output A. The statement dashboard

One message answering: what came in, what matched, what did not, what needs a person, and
what it is worth. Layout is defined in `templates/dashboard-layout.md`.

Rules:

- Every number is read, not computed from memory. Say how many pages you read when a figure
  comes from paging.
- Prefer the statement header closing balance over a summed total. It is authoritative and
  it is one read.
- If a figure cannot be obtained within a reasonable number of reads, say so and give what
  you have, with its coverage. A labelled partial figure is useful. An unlabelled one is a
  liability.
- Group unmatched lines by reason code, not as a flat list. Counts by reason are actionable.
  A list of forty lines is not.
- Close with what a person has to do next, and where.

### Output B. Transaction line detail

The inline detail for one line or a small set. Field list and ordering are defined in
`templates/transaction-line-fields.csv`. The fields that matter most, and that the customer
specifically asked for:

| Field | Source | Why it matters |
|---|---|---|
| Gross amount | `Ntry/AmtDtls/InstdAmt/Amt` | What the payer actually sent |
| Fees | `Ntry/Chrgs/TtlChrgsAndTaxAmt` | What the bank took |
| Net booked amount | `Ntry/Amt` | What arrived |
| Payment reference | `Refs/EndToEndId`, `RmtInf/Ustrd`, `RmtInf/Strd/CdtrRefInf/Ref` | What it was for |
| Payer | `RltdPties/Dbtr/Nm` | Who sent it. For a nonprofit, the donor |
| Exchange rate | `AmtDtls/CntrValAmt/CcyXchg/XchgRate` | Why the amount differs from the invoice |

Rules:

- Show gross, fees and net together on the same line. Presenting net alone is what the
  current state already does badly.
- If gross and fees are absent from the file, show the net and state that the bank did not
  supply the breakdown. **Do not derive a gross figure and present it as reported.** If you
  derive one, label it derived.
- If `Chrgs/Rcrd/ChrgInclInd` is true, the charge is already inside the booked amount. Do not
  subtract it again and do not display it as an additional deduction.
- Show the match status and, where matched, what it matched to. Reporting an existing match
  read from D365 is reporting. Suggesting one is matching, and is prohibited.
- Leave a blank field blank. Never fill it with a plausible value.

## Procedure

1. Establish the scope. One statement, one account for a period, or one line.
2. Read the statement header first. It gives identity, period, currency and balances in a
   single read, and the balances are authoritative.
3. Read the worksheet tabs for matched and unmatched counts. Page properly.
4. For a dashboard, group unmatched lines by reason code using the taxonomy from
   `match-exception-explainer`.
5. For line detail, read the fields in `templates/transaction-line-fields.csv` in the order
   given, and drop the ones marked as not shown by default.
6. Assemble one message using the layout template.
7. State coverage. If you read 3 pages of 12, say so.
8. End with the next action and the exact navigation path.

## Response format

Use the block order in `templates/dashboard-layout.md`. In summary:

```
Statement
  Account, statement id, period, currency, opening and closing balance.

Position
  Lines total, matched, unmatched, value in each. With coverage stated.

Needs attention
  Grouped by reason code, with counts and values. Highest severity first.

Detail
  Markdown table of lines, using the default field set.
  Gross, fees and net on the same row.

Next
  What a person does, and the exact navigation path.
```

Do not include an empty block. If nothing needs attention, say so in one line.

## Edge cases

| Situation | Handling |
|---|---|
| Statement has 4,000 lines | Do not render them. Give the dashboard, group by reason, offer detail on a subset |
| Total requested but paging incomplete | State the figure with its coverage, or use the header balance. Never present a partial as a total |
| Bank sent no fee or gross detail | Show net, state the breakdown was not supplied, request it from the bank |
| Batch booked entry with no per item detail | Show the entry with its `Btch/NbOfTxs` count and say the per-item detail is not in the file. This is reason code MX-18 |
| User asks for a chart or a card | Adaptive cards cannot carry live data. Offer a table instead |
| User asks what a line probably is | Refuse the identification. Show the fields and hand to `match-exception-explainer` |
| A field is empty | Leave it empty. Never fill it |
| User wants this emailed or scheduled | The agent reports in conversation. Scheduled distribution is a Power Automate job |
| Currency differs across lines | Group by currency. Never sum across currencies |
| User asks why a line is unmatched | Hand to `match-exception-explainer` |
| User asks to change what the dashboard shows | Point them at `templates/dashboard-layout.md` and `templates/transaction-line-fields.csv` |

## Tools

- D365 ERP MCP tool on the `shared_dynamicsax` connector, for statement headers, statement
  lines, worksheet tabs, vouchers and settled documents. 25 rows per call. Page everything.
- `ListErpDataEntities` on the same connector, to confirm a field is actually available
  before designing a column around it.
- No Dataverse tool is wired. Anything sourced from policy templates must be labelled as a
  template value, not a system value.

## Never claim

- a total from a single grid page
- a gross amount or fee the bank did not supply, unless labelled derived
- an exchange rate the bank did not supply
- a match the agent worked out itself
- that a card can display live data
- a 2026 Wave 1 new financial journal framework
- fuzzy logic matching, which is not a Microsoft term
- bulk approve and reject as generally available, it is private preview at 10.0.46
- any native import speed or performance figure

## What to change here

| To change this | Edit this file |
|---|---|
| The dashboard block order, headings, wording and which blocks appear | `templates/dashboard-layout.md` |
| Which fields appear on a transaction line, their labels, order, format and whether they show by default | `templates/transaction-line-fields.csv` |
| The paging, totalling and adaptive card rules | `reference/presentation-constraints.md` |
| Adding a customer-specific field such as a campaign code or a donor id | Add a row to `transaction-line-fields.csv` with its source path, then confirm the field exists in the bank file before relying on it |
| Making the dashboard shorter for daily use | Set `show_by_default` to No on the fields you do not need. That is the intended way to restyle it |
