# Latest bunker prices (`GET /commodity/prices/latest/token`)

HiFleet **latest commodity / bunker prices** — fetch hub bunker quotes (VLSFO / IFO / MGO) for voyage scenario estimation when the user does not supply `bunkerPrice`.

---

## Distribution

1. Data from **`api.hifleet.com`** only.
2. **`hifleet_api_key`** required; Query **`api_key`** or Header **`x-api-key`** (either one) — do not paste the full key in chat.
3. Prefer live API prices over fabricated bunker numbers.
4. If the user already gave bunker prices, do **not** overwrite them unless they ask to refresh from the API.

---

## Base URL

| Item | Default |
|------|---------|
| `{api}` | `https://api.hifleet.com` |

Resolve: `hifleet_api_base` → `HIFLEET_API_BASE` → default above.

**Endpoint**:

```text
GET {api}/commodity/prices/latest/token
```

Full default URL:

```text
https://api.hifleet.com/commodity/prices/latest/token
```

---

## When to call

In **`hifleet-voyage-scenario-estimator`**, call this API when `bunkerPrice` (or per-grade prices) is missing:

1. Fetch latest hub quotes from `data[]`.
2. Map grades into Skill inputs: **`priceVlsfo` → VLSFO**, **`priceMgo` → LSMGO/MGO**, **`priceIfo` → HSFO/IFO** (USD/MT unless `unit` says otherwise).
3. Pick a hub via `type` (e.g. `Singapore`, `Rotterdam`) — ask the user if the voyage region is unclear; do not invent a hub.

---

## Request

**`GET {api}/commodity/prices/latest/token`**

Method: **GET**

### Auth (pick one)

| Param / Header | Example | Required | Type | Notes |
|----------------|---------|----------|------|-------|
| Query `api_key` | `sk_live_xxx` | yes* | string | OpenClaw api_key |
| Header `x-api-key` | `sk_live_xxx` | no* | string | Same key; **either** Query `api_key` **or** Header `x-api-key` |

\* One of Query `api_key` or Header `x-api-key` is required.

### Example

```text
GET https://api.hifleet.com/commodity/prices/latest/token?api_key={key}
```

Or:

```text
GET https://api.hifleet.com/commodity/prices/latest/token
Header: x-api-key: {key}
```

---

## Response

Typical top-level fields: `status`, `msg`, `data[]`.

**Success** (as live API): `msg` is `SUCCESS`, or `status` is `"1"` / success, and `data` is an array.

### `data[]` fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Record id |
| `reportDate` | string | Price date (`YYYY-MM-DD`) |
| `title` | string | e.g. `Bunker Prices` |
| `type` | string | Bunker hub: `zhoushan`, `Singapore`, `Rotterdam`, `Fujairah`, `Houston`, … |
| `priceVlsfo` | number | VLSFO price (USD/MT typical) |
| `priceIfo` | number | IFO / HSFO price |
| `priceMgo` | number | MGO / LSMGO price |
| `diffSpread` | string | Spread delta (as returned) |
| `spread` | string | Spread (as returned) |
| `week` | string | Week change; may be empty |
| `month` | string | Month change; may be empty |
| `yoy` | string | Year-over-year; may be empty |
| `unit` | string | Unit label; may be empty (treat as USD/MT if empty and context is bunker) |
| `createTime` | string | Record create time |
| `createBy` | string | Author |
| `addandsub` | string | Extra numeric field (as returned) |

### Example body

```json
{
  "status": "1",
  "msg": "SUCCESS",
  "data": [
    {
      "id": "9377",
      "reportDate": "2026-07-07",
      "title": "Bunker Prices",
      "type": "Singapore",
      "priceVlsfo": 633,
      "priceIfo": 448,
      "priceMgo": 912,
      "diffSpread": "-48.0",
      "spread": "-20.60",
      "week": "",
      "month": "15.99",
      "yoy": "",
      "unit": "",
      "createTime": "2026-07-08 17:55:30",
      "createBy": "xiekeqin",
      "addandsub": "185.0"
    }
  ]
}
```

### Selection rules

| Case | Action |
|------|--------|
| Empty `data` | Tell user no bunker quote; ask for manual `bunkerPrice` |
| User names a hub | Match `type` (case-insensitive; e.g. Singapore / zhoushan) |
| Hub unclear | List available `type` values and ask user to pick |
| Single-grade estimate | Use the grade the voyage needs (often `priceVlsfo` for sea fuel) |
| Multi-grade estimate | Map `{ VLSFO: priceVlsfo, LSMGO: priceMgo, HSFO: priceIfo }` into Skill `bunkerPrice` |

Always cite **`type`** and **`reportDate`** when quoting prices so the user knows hub and as-of date.

**Never** fabricate bunker rows or invent hub prices when the API fails or returns empty.

---

## Errors

Localized short message (e.g. `token is empty` / auth failure); never fabricate price rows. If the key is missing, prompt to configure `hifleet_api_key` — do not invent results.
