# Route by position (`GET /routepoints/routebyposition/token`)

HiFleet **planned route by coordinates** — compute a sea route between start/end positions (optional via-points and avoid-area IDs). Use for voyage scenario estimation when `distanceNm` / ECA / track geometry are missing.

---

## Distribution

1. Data from **`api.hifleet.com`** only.
2. **`hifleet_api_key`** required; Query **`api_key`** and **`usertoken`** (same key is OK) — do not paste the full key in chat.
3. **`start`** and **`end`** are required; never invent distances or waypoints when the call fails.
4. Resolve port names → coordinates first via **`SUGGESTION_LOCATION_API.md`** when the user only gives port names.

---

## Base URL

| Item | Default |
|------|---------|
| `{api}` | `https://api.hifleet.com` |

Resolve: `hifleet_api_base` → `HIFLEET_API_BASE` → default above.

**Endpoint**:

```text
GET {api}/routepoints/routebyposition/token
```

Full default URL:

```text
https://api.hifleet.com/routepoints/routebyposition/token
```

Related (N2218 form): `POST /hifleetrouteapi/getNewRoute` — same distance semantics (`dis` / `nmile` / `ecadis`); prefer **this** OpenClaw token API when calling from the voyage-scenario skill unless the form wrapper is already in use.

---

## When to call

In **`hifleet-voyage-scenario-estimator`**:

1. Load/discharge (or leg) coordinates are known: `{ lng, lat }` or `{ lon, lat }`.
2. Scheme needs `distanceNm` / `ecaDistanceNm`, or a track for Suez / Cape / detour comparison.
3. Optional: set **`avoidareaid`** to steer around canals/straits (e.g. Suez `669`, Dover `671`).
4. Optional: set **`viewpoint`** for via-points the route must pass.

Without coordinates → call **`SUGGESTION_LOCATION_API.md`** first; do **not** put port names into `start` / `end`.

---

## Request

**`GET {api}/routepoints/routebyposition/token`**

Method: **GET**

### Query

| Param | Example | Required | Type | Notes |
|-------|---------|----------|------|-------|
| `api_key` | `sk_xxx` | yes | string | OpenClaw api_key |
| `usertoken` | `sk_xxx` | yes* | string | Required by live API; use the same OpenClaw key when no separate user token is available |
| `start` | `-81.01,13.16` | yes | string | Start position: **`longitude,latitude`** |
| `end` | `86.90,11.23` | yes | string | End position: **`longitude,latitude`** |
| `avoidareaid` | `669,671` | no | string | Avoid-area IDs, comma-separated |
| `viewpoint` | *(empty or lon,lat)* | no | string | Intermediate via-point(s); format same as position string when used |

\* Live gateway returns `Required String parameter 'usertoken' is not present` if `usertoken` is omitted (even when `api_key` is set).

### Example

```text
GET https://api.hifleet.com/routepoints/routebyposition/token?api_key={key}&usertoken={key}&start=-81.01,13.16&end=86.90,11.23&avoidareaid=669,671&viewpoint=
```

### Coordinate rules

- Order is always **`lon,lat`** (same as Skill `{ lng, lat }` / `{ lon, lat }`).
- Build from confirmed port coords, e.g. Shanghai `121.5841333,31.3797833`.
- Empty `viewpoint` is allowed (omit or pass blank).

### Common avoid-area IDs

| ID | Name |
|----|------|
| `669` | Suez Canal |
| `671` | Dover Strait |
| `678` | Strait of Malacca |
| `696` | Taiwan Strait |

Use IDs from product config / prior API responses when available; do not invent IDs.

---

## Response

Typical top-level fields: `status`, `start`, `end`, `viewpoint`, `nmile`, `passAvoidArea[]`, `waypoints[]`.

**Success**: `status` is `success` (or equivalent success / `"1"`), and distance is available from `waypoints[0].dis` and/or `nmile`.

### Top-level fields

| Field | Type | Notes |
|-------|------|-------|
| `status` | string | e.g. `success` |
| `start` | string | Echo start `lon,lat` (may be normalized) |
| `end` | string | Echo end `lon,lat` |
| `viewpoint` | string | Echo via-point; may be empty |
| `nmile` | number | Total distance (nm); fallback if `waypoints[0].dis` missing |
| `passAvoidArea` | array | Avoid/pass areas related to the route |
| `waypoints` | array | Route option(s); use **`waypoints[0]`** for primary distance |

### `passAvoidArea[]`

| Field | Type | Notes |
|-------|------|-------|
| `areaid` | number | Area id (e.g. `669`) |
| `name` | string | Name (CN) |
| `ename` | string | Name (EN) |
| `gis` | string | WKT polygon |

### `waypoints[0]` (primary option)

| Field | Type | Notes |
|-------|------|-------|
| `dis` | number | Distance nm — **prefer for `distanceNm`** |
| `ecadis` | number | ECA distance nm — **prefer for `ecaDistanceNm`** |
| `ecalist` | array | ECA segments (`dis`, `name`, `ename`) |
| `piracydis` | number | Piracy / high-risk distance nm |
| `piracylist` | array | Piracy segments (`dis`, `name`, `ename`) |
| `waypoints` | array | Track points: each `[lon, lat]` |

### Example body (trimmed)

```json
{
  "end": "85.76410072157188,4.403802717417645",
  "nmile": 7321,
  "passAvoidArea": [
    {
      "areaid": 671,
      "ename": "Dover Strait",
      "gis": "POLYGON((1.0025 50.9584,1.4172 50.496,2.2742 50.6582,1.8622 51.322,1.4749 51.3049,1.0025 50.9584))",
      "name": "多菲尔海峡"
    },
    {
      "areaid": 669,
      "ename": "Suez Canal",
      "gis": "POLYGON((32.5099 30.2917,32.5195 30.0287,32.6349 30.0346,32.5573 30.2893,32.5099 30.2917))",
      "name": "苏伊士运河"
    }
  ],
  "start": "3.812706152462681,54.459206024127575",
  "status": "success",
  "viewpoint": "",
  "waypoints": [
    {
      "dis": 7321.5,
      "ecadis": 518.5,
      "ecalist": [
        {
          "dis": 518.5,
          "ename": "North Sea&Baltic emission control area",
          "name": "北海波罗的海排放控制区"
        }
      ],
      "piracydis": 1569.1,
      "piracylist": [
        {
          "dis": 1569.1,
          "ename": "High risk areas of Indian Ocean",
          "name": "印度洋高风险区"
        }
      ],
      "waypoints": [
        [3.812706152462681, 54.459206024127575],
        [85.76410072157188, 4.403802717417645]
      ]
    }
  ]
}
```

### Normalization for voyage estimate

| Skill field | Source |
|-------------|--------|
| `distanceNm` | `waypoints[0].dis`，else `nmile` |
| `ecaDistanceNm` | `waypoints[0].ecadis` (else top-level `ecadis` if present) |
| `route.requestParams` | Echo `start`, `end`, `avoidareaid`, `viewpoint` |
| `route.response` | Keep raw JSON for audit |

Same priority as **TC-07**: `waypoints[0].dis` over `nmile`; `waypoints[0].ecadis` over top-level `ecadis`.

For **Suez / Cape / detour** comparisons, call this API **per scheme** with different `avoidareaid` (or omit). If a constraint is unsupported, say so and ask for manual `distanceNm` — never invent nm.

**Never** fabricate `dis`, track points, or avoid-area geometry when the API fails or returns non-success.

---

## Errors

Localized short message (e.g. `token is empty` / auth failure / invalid coords); never fabricate route rows. Missing key → prompt to configure `hifleet_api_key`. Missing coords → resolve ports via **`SUGGESTION_LOCATION_API.md`** first.
