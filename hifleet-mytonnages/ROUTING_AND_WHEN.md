# Routing and when to run

## Routes (this skill only)

| Route | Meaning |
|-------|---------|
| **A** | Mailbox open tonnage / cargo |
| **C** | Pre-arrival vessels at a port |

**Liner schedule** (bulk / Ro-Ro / container) → install and use **`hifleet-schedule`**.

**Public open tonnage/cargo** (HiFleet marketplace, fully open) → **`hifleet-opentonnages`**.

---

### Route A — mailbox

- Triggers: “in my mail”, sender, open tonnage/cargo from inbox.  
- Needs: email + memory (recommended) + enrich API key.  
- Docs: **`WORKFLOW_2_MAIL.md`**, **`MAIL_PARSE_SCHEDULE.md`**.

### Route C — pre-arrival

- Triggers: pre-arrival, ETA, vessels arriving at port (not “in my mail”).  
- Needs: **`hifleet_api_key`**.  
- Docs: **`DESTINATION_SEARCH_API.md`**, **`FULL_LIST_POLICY.md`**.

---

## When to run

| Situation | Action |
|-----------|--------|
| First install | **`FIRST_SETUP.md`** |
| Liner / line schedule question | **`hifleet-schedule`** skill |
| Mail + pre-arrival in one question | Run **A** and **C** separately |
| Parse / JSON / token error | **`LLM_TOKEN_LIMITS.md`** + localized message |

---

## User language

**`LOCALIZATION.md`**: English default; translate system text to user locale; keep business data untranslated.
