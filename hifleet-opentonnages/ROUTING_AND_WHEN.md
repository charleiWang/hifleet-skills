# Routing and when to run

## Routes (this skill only)

| Route | Meaning | API |
|-------|---------|-----|
| **V** | HiFleet **public open tonnage** | `VESSEL_SEARCH_API.md` |
| **G** | HiFleet **public cargo** | `CARGO_SEARCH_API.md` |

---

### Route V — public open vessels

- **Triggers**: public/open tonnage, platform ship list, HiFleet open vessels, “what bulkers are open”, not “in my mail”.
- **Needs**: `hifleet_api_key`.
- **Never**: mailbox SQLite, email parse, **`/unlock`**.

### Route G — public cargo

- **Triggers**: public/open cargo, platform cargo list, charter cargo on HiFleet, not “in my mail”.
- **Needs**: `hifleet_api_key`.
- **Never**: mailbox, **`/unlock`**.

---

## Disambiguation

| User says | Skill |
|-----------|--------|
| **My mail** / sender / inbox | **hifleet-mytonnages** (A) |
| **Liner / line** schedule | **hifleet-schedule** |
| **Pre-arrival / ETA** at port | **hifleet-mytonnages** (C) |
| **Public / platform / HiFleet** open tonnage or cargo | **hifleet-opentonnages** (V/G) |

---

## When to run

| Situation | Action |
|-----------|--------|
| First install | **`FIRST_SETUP.md`** |
| User wants archive + distance on public rows | **`ENRICH_OPENTONNAGES.md`** after list fetch |
| List query | **`FULL_LIST_POLICY.md`** — paginate to **`total`** |

---

## Language

**`LOCALIZATION.md`**: English default; localize system messages; keep business data verbatim.
