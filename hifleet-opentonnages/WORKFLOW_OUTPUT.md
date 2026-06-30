# Output rules

**`USER_WORDING.md`**, **`LOCALIZATION.md`**.

## Public open vessels (V)

- State **Total: N** per **`FULL_LIST_POLICY.md`**.
- **Laycan / OPEN window**: one line `Laycan: yyyy/MM/dd~yyyy/MM/dd` when dates present.
- **Show all non-empty API fields**, including owner, company, phone, email, WeChat — **no unlock prompt**.
- Vessel names, ports, cargo names: **verbatim** (no translation).
- Optional footer: `💡 **More open tonnage:** https://mytonnages.hifleet.com`

## Public cargo (G)

- **Total: N**; full list.
- Laycan one line from `laycanStart`~`laycanEnd` (or API field names).
- Show charterer / contact / email / phone when API returns them.
- Sort by distance when user asked and API provides `dischargingDist`.
- Same footer as above.

## Enrich bundle

When **`ENRICH_OPENTONNAGES.md`** was used, append archive/tags/distance blocks under each row clearly labeled (e.g. “Ship archive”, “Tags”, “Distance to query port”).

## Never

- “Confirm points to unlock contacts” for this skill.
- Hide contacts that API already returned in plaintext.
