# Output rules

Use **`USER_WORDING.md`** and **`LOCALIZATION.md`**.

## Route C (pre-arrival)

- Full list per **`FULL_LIST_POLICY.md`**.  
- Show distance, ETA, vessel names **as in API** (do not translate).

## Route A (mailbox)

- Sender, time, subject + structured fields.  
- **Dedup**: **`WORKFLOW_2_MAIL.md` §2.5.1**.  
- Show **`联系电话` / `即时通讯`** when present in DB (from original-body extract).  
- Laycan one line for cargo / open windows.  
- **`preview_url`** on each row when mail preview server is running — link **「查看原邮件」** per **`MAIL_PREVIEW.md`**.
- **`webmail_url`** when `imap_host` maps to a known webmail — link **「在网页邮箱中打开」** (browser must already be logged in).

## Liner schedule

Use skill **`hifleet-schedule`** and its **`WORKFLOW_OUTPUT.md`**.

## Fixed footer (route A)

`💡 **More tonnage/cargo:** https://mytonnages.hifleet.com`
