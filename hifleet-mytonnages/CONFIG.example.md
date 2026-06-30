# config.json example (mytonnages — routes A + C)

```json
{
  "hifleet_api_key": "from HiFleet website",
  "hifleet_charter_api_base": "https://api.hifleet.com/openclaw/vessel/charter",
  "charter_enrich_url": "https://api.hifleet.com/openclaw/vessel/charter/enrich-row",
  "mail_parse_interval_minutes": 10,
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "imap_mailbox": "INBOX",
  "email": "user@example.com",
  "email_password": "app password (local only)",
  "mail_preview_host": "0.0.0.0",
  "mail_preview_port": 8765,
  "mail_preview_base_url": "http://localhost:8765",
  "mail_preview_token": ""
}
```

**Liner schedule API base** (`hifleet_liner_api_base`) is for **`hifleet-schedule`**, not this skill.

Optional locale: environment **`HIFLEET_USER_LOCALE`** (`en`, `zh`, `zh-TW`, …).
