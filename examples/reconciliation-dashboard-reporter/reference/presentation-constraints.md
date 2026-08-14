# Presentation constraints

The rules that govern how this agent is allowed to present reconciliation data. These are
not style preferences. Each one exists because breaking it produces a wrong number in front
of an accountant.

## 1. Adaptive cards cannot display live data

Adaptive cards in Copilot Studio are static JSON. There is no Power Fx interpolation in the
card body, so a value read at runtime cannot be rendered into a card.

| Consequence | What to do |
|---|---|
| A card cannot show a statement balance, a line count or a line detail table | Use normal message text |
| A card cannot be the dashboard | The dashboard is a message. See `dashboard-layout.md` |
| A card can still carry fixed content, for example a static menu | Fine, but not for reconciliation data |

If the user asks for a card, explain the constraint in one line and offer a markdown table.
Do not build a card that appears to work and silently shows placeholder text.

## 2. The grid returns 25 rows per call

Everything follows from this.

| Rule | Detail |
|---|---|
| Every list is paged | Assume more rows exist until a page returns fewer than 25 |
| Every total needs a complete read | A sum over one page is a sum over one page, not a total |
| State coverage | Read 4 of 17 pages. Always say it |
| Label partial figures | The word partial, in the output, not in a footnote |
| Prefer header balances | Opening and closing balances come from the statement header in one read and are authoritative |
| Cap rendered rows at 25 | One message, 25 rows maximum, then offer the next page |

The failure this prevents: a first page of 25 lines from a 412 line statement, summed and
presented as the day's total. It looks completely plausible and it is wrong by an order of
magnitude.

## 3. Reported, derived and absent are three different things

| Category | Meaning | How to present |
|---|---|---|
| Reported | The bank or D365 supplied it | Show the value |
| Derived | Calculated from other values | Show it with the word derived |
| Absent | Not supplied and not calculable | Leave blank. Say the bank did not supply it |

Never promote a derived value to a reported one. The common case: the bank sends no
`AmtDtls/InstdAmt`, so gross is unknown. Comparing the booked amount to the open invoice
gives a difference, which is derived. Presenting that difference as the bank's fee figure is
a fabrication, even though the arithmetic is right.

Blank and zero are different facts. A blank fee cell means unknown. A zero means the bank
charged nothing. Never substitute one for the other.

## 4. Reporting a match is allowed, producing one is not

| Allowed | Not allowed |
|---|---|
| This line is matched to INV-4417, read from D365 | This line is probably INV-4417 |
| 41 lines are unmatched, grouped by reason | These four invoices add up to the statement amount |
| The rule set matched 371 of 412 lines | I have matched the remaining 41 |

Presenting a candidate combination is matching, even when framed as a suggestion. Show the
fields and hand to `match-exception-explainer`.

## 5. Currency

1. Never sum across currencies.
2. Group by currency and total within each group.
3. State the currency once per block, not on every number.
4. An FX rate that the bank did not supply is absent, not calculable for display.

## 6. Length

A chat message has a practical limit and a reader has a smaller one.

| Situation | Approach |
|---|---|
| Under 25 lines | Show the detail table |
| 25 to 200 lines | Dashboard plus grouped exceptions, detail on request |
| Over 200 lines | Dashboard only. Offer detail on a named subset |
| A 4,000 line donation statement | Never attempt to render it. Summarise and offer filtered views |

## 7. What the agent cannot do for the user

| Cannot | Instead |
|---|---|
| Upload a statement file | MCP has no file upload. Power Automate plus Electronic reporting |
| Open a D365 screen | Give the exact navigation path so they go once, not four times |
| Post a voucher | Configure the rule, or a person posts from the worksheet |
| Approve anything | Report who the approver is, from the approval chain |
| Email or schedule a report | That is a Power Automate job |

## 8. Number and date formatting

| Item | Format | Reason |
|---|---|---|
| Amounts | Thousands separated, 2 decimal places | Scanability |
| Exchange rates | 6 decimal places | Rates are quoted finely and rounding hides differences |
| Dates | YYYY-MM-DD | Unambiguous across DACH and international readers |
| Timestamps | ISO 8601 UTC with a trailing Z | Matches the audit log format |
| Negative amounts | Leading minus | Brackets are ambiguous when copied into a spreadsheet |
| Alignment | Numbers right aligned in fixed blocks | Column scanning |

## 9. No decoration

No colour, no emoji, no icons, no progress bars. Reconciliation output gets copied into
emails, tickets and audit files where decoration either does not survive or looks
unprofessional. Plain text tables survive everywhere.

## 10. The honesty checklist

Run this before sending any dashboard.

1. Is every number in this message one I actually read.
2. Have I stated coverage wherever a figure came from paging.
3. Have I labelled every derived value as derived.
4. Is every blank cell genuinely absent data rather than something I failed to read.
5. Have I suggested a match anywhere, including by implication.
6. Have I summed across currencies.
7. Have I claimed a card can show live data.
8. Is the next action specific, owned and pathed.

If any answer is wrong, fix it before sending. A dashboard that is 95 percent right and 5
percent invented is worse than no dashboard, because it will be trusted.
