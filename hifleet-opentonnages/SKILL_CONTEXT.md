# Skill context — hifleet-opentonnages

## What this is

HiFleet **public** open tonnage (vessels for hire) and **public** cargo listings on the platform — **not** the user’s private mailbox.

## Commercial model (v1.0)

- List/search APIs return **plaintext, fully open** records (contacts included). **No decrypt / unlock step.**
- Optional **`enrich-row`** bundles **vessel archive**, **tags**, and **port-distance** context — billed via the user’s **`hifleet_api_key`** (same as other OpenClaw charter APIs).
- Do **not** describe contacts as “hidden until unlock”.

## API root

`https://api.hifleet.com/openclaw/vessel/charter` (`hifleet_charter_api_base` / `HIFLEET_CHARTER_API_BASE`).

| Route | Endpoint |
|-------|----------|
| **V** Open vessels | `POST /vessels/search` |
| **G** Open cargo | `POST /cargo/search` |
| Enrich (optional) | `POST /enrich-row` |

## Sibling skills

| Skill | Scope |
|-------|--------|
| **hifleet-mytonnages** | User mailbox A + pre-arrival C |
| **hifleet-schedule** | Liner schedules (may still use liner `/unlock` — separate product) |
| **hifleet-opentonnages** | **This** — public open vessel + cargo |
