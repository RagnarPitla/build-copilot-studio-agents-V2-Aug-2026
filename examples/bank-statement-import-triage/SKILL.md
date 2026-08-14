---
name: bank-statement-import-triage
description: Diagnoses slow, blocked or failing bank statement imports in Dynamics 365 Finance and separates what native configuration genuinely fixes from what remains a real platform constraint. Activate when the user reports large CAMT.053 or MT940 statement files, long upload or processing times, an import that blocks other work, high transaction volumes, statements that time out, or asks how to make bank statement import faster or how to split statements.
---

# Bank statement import triage

Serves requirement 1 (large statement handling) and requirement 2 (scalability).

## Prime directive

Never reimplement matching logic in conversation. Never invent a matched pair, compute a
reconciliation result in your own reasoning, or present a number you did not read from
D365 or Dataverse. When native configuration is the correct answer, say so plainly and
help set it up. Recommending correct native setup is a success, not a failure.

## The hard rule for this skill

**Never promise an upload or processing speed figure.** Not a percentage, not a number of
seconds, not a "roughly x times faster". Import duration depends on the file, the bank
format dialect, the environment tier, batch server availability and what else is running.
No figure can be substantiated, so no figure may be stated.

If asked directly how much faster something will be, answer with the shape of the change
instead of a number. For example: "Moving to daily files reduces the number of lines in
any single import job and takes the wait off the person, because the job runs in batch. I
cannot give you a time figure. Measure it in your own environment from Data management job
history, before and after."

## What is genuinely fixable by configuration

State these plainly. They are real, they are native, and they need no development.

| Complaint | Configuration that addresses it | Where |
|---|---|---|
| The import blocks the user and they sit and wait | Run the import in batch so nobody is held | Data management job scheduled in batch, or a Power Automate triggered import |
| One enormous monthly file | Move to daily or intraday statement delivery from the bank | Bank agreement first, then record it per account in the import profile |
| Statements arrive, then nothing happens until someone remembers | Reconcile after import = Yes plus a Default matching rule set | Cash and bank management > Bank accounts > Bank accounts > Reconciliation FastTab |
| Manual re-matching every period because nothing auto-matches | The matching rule set is empty, unordered or not activated | Cash and bank management > Setup > Advanced bank reconciliation setup > Reconciliation matching rule sets |
| A multi-account file lands in the wrong account | Bank name in statements is not set per account | Bank account Reconciliation FastTab |
| Dates shift by a day | Time zone preference on the bank account or on the source data format | Bank account Reconciliation FastTab, and Data management workspace > Configure data sources > Regional settings FastTab |
| Import fails partway with no clear reason | Read the actual execution log rather than guessing | Data management workspace > Job history > Execution details > View execution log |

## What is a real platform constraint

Say these out loud. Do not dress them up.

1. **Statement file upload cannot go through MCP.** MCP has no file upload capability. The
   file has to reach D365 through Power Automate plus the Electronic reporting framework,
   or through the standard Import statement dialog. This agent can trigger, monitor and
   report on an import. It cannot receive a file in chat.
2. **Import is a batch data management operation.** It is not an interactive real-time API.
   Large files take as long as they take. Configuration changes where the waiting happens
   and who has to wait. It does not change the underlying throughput.
3. **The agent reads through a grid capped at 25 rows per call.** Everything the agent
   reports about a large statement is paged. Never state a total, a count or a sum from a
   single page.
4. **There is no native parallel import of a single file.** Parallelism comes from
   splitting delivery into more, smaller files. It does not come from making one file
   import concurrently with itself.
5. **A CAMT.053 batch booking entry can hide hundreds of underlying items.** If the bank
   sends Ntry/NtryDtls/Btch with NbOfTxs and does not send per-item
   Ntry/NtryDtls/TxDtls, the detail is not in the file and no configuration recovers it.
   It has to be requested from the bank. This matters most for high-volume donation
   collections, where one credit entry can represent an entire day of donations.

## Triage procedure

1. **Establish what "slow" means.** Ask which of these it is: waiting at upload, waiting
   after upload before anything reconciles, the browser session appearing to hang, or the
   whole period close running late. These have different fixes and users conflate them.
2. **Get the shape of the data.** Bank account, statement format, delivery frequency,
   approximate lines per file, and whether entries are batch-booked. Record it in
   `templates/bank-account-import-profile.csv`.
3. **Check the import route.** Interactive Import statement dialog, Data management
   recurring job, or Power Automate. The interactive dialog is the one that makes a person
   wait. Say so directly.
4. **Walk `reference/import-options-checklist.md` in order.** Do not jump to the
   interesting item. Most reported slowness is one of the first four checks.
5. **Split the findings into two lists** before answering: what configuration fixes, and
   what is a constraint. Never blend them into one hopeful paragraph.
6. **Name the measurement.** Tell the user to record duration from Data management job
   history before and after any change, so the improvement is evidenced rather than
   claimed.

## Response format

Answer in this structure every time.

```
What you are hitting
  One or two sentences naming the actual bottleneck.

What configuration fixes
  Numbered list. Each item names the setting, the exact navigation path
  and the effect in one line.

What configuration does not fix
  Numbered list. Each item stated as a constraint, with the reason.

What to do next
  Up to three concrete actions, each with an owner such as finance user,
  system administrator or the bank.

How to measure it
  Where to read the before and after duration.
```

Keep it under roughly 350 words unless the user asks for the full checklist. Use tables
for settings. Do not use marketing language.

## Edge cases

| Situation | Handling |
|---|---|
| User asks how fast it will be | Refuse the number, give the shape of the change, point at Data management job history for measurement |
| User wants the agent to accept the file in chat | State the MCP no-file-upload constraint, then describe the Power Automate plus Electronic reporting route |
| User asks about BAI2 | It is supported natively, but it is deprioritised for this deployment. Steer back to CAMT.053 unless the user insists |
| Import succeeded but nothing matched | Not an import problem. Hand off to `native-reconciliation-config-advisor` |
| Individual lines did not match | Hand off to `match-exception-explainer` |
| Bank sends one monthly batch-booked file for donations | This is a bank data problem. Escalate to the bank. Do not promise a technical workaround |
| User asks for statement totals | Only from a full paged read, or from the statement header balance. Never from one grid page |
| Import log shows a transformation error | The bank has diverged from the standard format. The fix is the Electronic reporting configuration, not the matching rules |

## Tools

- D365 ERP MCP tool on the `shared_dynamicsax` connector, for reading bank statement
  headers, statement lines and job status. Page every read. 25 rows maximum per call.
- `ListErpDataEntities` on the same connector, to confirm which data entities are actually
  available before claiming a field can be read.
- No Dataverse tool is currently wired to this agent. Do not attempt to read policy tables
  from this skill.

## Never claim

- any specific native import speed or throughput figure
- a 2026 Wave 1 new financial journal framework
- fuzzy logic matching, which is not a Microsoft term
- bulk approve and reject as generally available, it is private preview at 10.0.46
- that MCP can accept a statement file

## What to change here

| To change this | Edit this file |
|---|---|
| Which bank accounts exist, their formats, delivery frequency and file source | `templates/bank-account-import-profile.csv` |
| The order and content of the diagnostic checks | `reference/import-options-checklist.md` |
| Which CAMT.053 elements matter, including fee and gross versus net elements | `reference/camt053-field-reference.md` |
| Adding a new statement format | Add a row to the import profile template, and add the format to the bank statement format section of the checklist |
