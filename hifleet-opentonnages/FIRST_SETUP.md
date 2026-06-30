# First setup

## Capability

**HiFleet public open tonnage + public cargo** (marketplace data). Requires **`hifleet_api_key`** only — **no mailbox**.

| Question type | Route |
|---------------|--------|
| Public / platform **open vessels** | **V** |
| Public / platform **cargo** | **G** |

**Not this skill**: my mail → **hifleet-mytonnages**; liner schedule → **hifleet-schedule**; pre-arrival → **hifleet-mytonnages**.

## Config

```json
{
  "hifleet_api_key": "from HiFleet website",
  "hifleet_charter_api_base": "https://api.hifleet.com/openclaw/vessel/charter",
  "charter_enrich_url": "https://api.hifleet.com/openclaw/vessel/charter/enrich-row"
}
```

Get key at [mytonnages.hifleet.com](https://mytonnages.hifleet.com).

## v1.0 product note (tell users)

Public listings are **fully open** — contacts and company info are included in search results. Optional **enrich-row** adds ship archive, tags, and port distance (uses API points).

## Language

`HIFLEET_USER_LOCALE` / `OPENCLAW_USER_LOCALE` — see **`LOCALIZATION.md`**.
