---
name: hifleet-opentonnages
version: 1.0.0
description: >
  HiFleet public open tonnage and cargo marketplace (fully open API data, no unlock/decrypt).
  Optional enrich-row for vessel archive, tags, and port distance. Requires hifleet_api_key.
metadata:
  openclaw:
    homepage: https://mytonnages.hifleet.com
    requires:
      anyBins:
        - python
        - python3
---

## Read first

**`SKILL_CONTEXT.md`**, **`ROUTING_AND_WHEN.md`**, **`LOCALIZATION.md`**.

**Not this skill**: private mailbox tonnage → **`hifleet-mytonnages`**; liner schedules → **`hifleet-schedule`**; pre-arrival → **`hifleet-mytonnages`** (route C).

**API Key**: **`FIRST_SETUP.md`**.

**Full list (mandatory)**: **`FULL_LIST_POLICY.md`**.

**No unlock**: responses are **fully public** — show contacts and company fields as returned. **Do not** call `/unlock`.

---

## Query steps

### Open vessels (route V)

1. **`ROUTING_AND_WHEN.md`** → **`VESSEL_SEARCH_API.md`**
2. Optional value-add: **`ENRICH_OPENTONNAGES.md`** (`enrich-row` for archive / tags / port distance)

### Open cargo (route G)

1. **`ROUTING_AND_WHEN.md`** → **`CARGO_SEARCH_API.md`**
2. Optional: **`ENRICH_OPENTONNAGES.md`**

### Output

**`WORKFLOW_OUTPUT.md`**, **`USER_WORDING.md`**

---

## Package index

```text
hifleet-skills/hifleet-opentonnages/
├── SKILL.md
├── SKILL_CONTEXT.md
├── LOCALIZATION.md
├── ROUTING_AND_WHEN.md
├── FIRST_SETUP.md
├── VESSEL_SEARCH_API.md
├── CARGO_SEARCH_API.md
├── ENRICH_OPENTONNAGES.md
├── FULL_LIST_POLICY.md
├── WORKFLOW_OUTPUT.md
├── USER_WORDING.md
├── CONFIG.example.md
├── scripts/opentonnages_tool.py
├── scripts/i18n_messages.py
└── PUBLISH.md
```
