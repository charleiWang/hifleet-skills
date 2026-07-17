# Port location suggest (`GET …/ports/suggest/location`)

HiFleet **port location suggest** — resolve a port keyword to **`portId`**, name, and **lat/lon** for voyage scenario estimation (load/discharge coordinates and port IDs).

---

## Distribution

1. Data from **`api.hifleet.com`** only.
2. **`hifleet_api_key`** required; Query **`api_key`** or Header (`x-api-key` / `Authorization: Bearer`) — do not paste the full key in chat.
3. Empty `keyword` returns an empty list; never invent ports from a blank keyword.
4. Multiple hits → ask the user to confirm; **never** guess `portId` or coordinates.

---

## Base URL

| Item | Default |
|------|---------|
| `{liner}` | `https://api.hifleet.com/openclaw/vessel/charter/liner` |

Resolve: `hifleet_liner_api_base` → `HIFLEET_LINER_API_BASE` → default above.

**Endpoint**:

```text
GET {liner}/ports/suggest/location
```

Full default URL:

```text
https://api.hifleet.com/openclaw/vessel/charter/liner/ports/suggest/location
```

---

## When to call

In **`hifleet-voyage-scenario-estimator`**, call this API when the user names a load/discharge port but **coordinates** or **`portId`** are missing:

1. Port name → resolve **`portId`**, **`lat`**, **`lon`** (map to `lng` if needed).
2. With coordinates, call the **port distance API** (`POST /hifleetrouteapi/getNewRoute`) — see main Skill § Port distance API.
3. **Do not** use `portguide/getPort/token` or other port-guide APIs for this step.

Call once per port (separate `keyword` for load and discharge).

Distinct from legacy **`GET {liner}/ports/suggest`** (portId only): this path is **`…/ports/suggest/location`** and returns lat/lon for distance estimation.

---

## Request

**`GET {liner}/ports/suggest/location`**

### Query

| Param | Example | Required | Type | Notes |
|-------|---------|----------|------|-------|
| `api_key` | `sk_xxx` | yes | string | OpenClaw auth key; also Header: `x-api-key` or `Authorization: Bearer sk_xxx` |
| `keyword` | `Shanghai` | no | string | Port keyword (**CN or EN**); empty → empty list |
| `from` | `0` | no | string | Page offset, default `0` |
| `size` | `5` | no | string | Page size, default `5`; downstream max **10** |
| `cjwharf` | `0` | no | string | Include Yangtze River wharves: `0` no (default), `1` yes |
| `i18n` | `cn` | no | string | Locale: `cn` / `en`, default `cn` |

### Example

```text
GET https://api.hifleet.com/openclaw/vessel/charter/liner/ports/suggest/location?api_key={key}&keyword=Shanghai&from=0&size=5&cjwharf=0&i18n=cn
```

Defaults: `from=0`, `size=5` (raise up to `10` if the user must pick among hits); keep `cjwharf=0` unless Yangtze wharves are needed.

---

## Response

Typical top-level fields: `msg`, `status`, `total`, `data[]`, `timestamp` (optional `s402`).

**Success** (as live API): `msg` is `SUCCESS`, or `status` is `"1"` / success, and `data` is an array.

### `data[]` fields

| Field | Type | Notes |
|-------|------|-------|
| `portId` | string | Port ID for downstream filters |
| `portName` | string | English name (often with country suffix, e.g. `Shanghai,CN`) |
| `portNameCn` | string \| null | Chinese name; may be `null` |
| `lat` | number | Latitude |
| `lon` | number | Longitude (map to `lng` for distance API) |
| `country` | string | Country name (EN) |
| `countryNameCn` | string | Country name (CN) |
| `countryCodeIso2` | string | ISO2, e.g. `CN` |
| `timeZone` | string | e.g. `UTC+08:00` |
| `timeZoneName` | string | e.g. `+8` |
| `_score` | number | Relevance score; prefer earlier rows when already sorted |

### Example body

```json
{
  "msg": "SUCCESS",
  "total": 4,
  "data": [
    {
      "country": "People's Republic Of China",
      "countryCodeIso2": "CN",
      "timeZoneName": "+8",
      "countryNameCn": "中国",
      "timeZone": "UTC+08:00",
      "lon": 121.5841333,
      "portName": "Shanghai,CN",
      "portId": "27999",
      "_score": 197.02026,
      "portNameCn": "上海,CN",
      "lat": 31.3797833
    }
  ],
  "s402": null,
  "status": "1",
  "timestamp": 1784079658177
}
```

### Selection rules

| Case | Action |
|------|--------|
| Empty `data` / `total` 0 | Tell user no match; ask for another keyword or spelling check |
| Single hit | Use `data[0]`: `portId`, `lat`, `lon` |
| Multiple hits | **In `hifleet-voyage-scenario-estimator`**: temporarily use **`data[0]`** as effective coords/`portId`, and state which port was auto-selected. Otherwise list candidates and ask the user. |
| Distance API input | `{ "lng": lon, "lat": lat }` → then **`ROUTEBYPOSITION_TOKEN_SKILL.md`** for voyage distance |

**Never** fabricate `portId` or coordinates when the API returns empty.

---

## Errors

Localized short message (e.g. `token is empty` / auth failure); never fabricate port rows. If the key is missing, prompt to configure `hifleet_api_key` — do not invent results.
