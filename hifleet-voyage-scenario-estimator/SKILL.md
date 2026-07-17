---
name: hifleet-voyage-scenario-estimator
version: 1.0.0
description: Guides quick voyage scenario estimation from cargo quantity, load/discharge ports, freight rate, bunker price, vessel speed, and port charges. Use when the user asks to estimate voyage days, fuel cost, port cost, TCE, demurrage/despatch sensitivity, or compare Suez / Cape / detour routing options.
---

# Voyage Scenario Estimator

## Scope

Quick voyage-scenario estimates from a small set of inputs:

```text
cargo quantity, load/discharge ports, freight rate, bunker price, speed, port charges
```

Outputs must cover:

```text
voyage days
fuel cost
port cost
TCE
demurrage / despatch sensitivity
Suez / Cape / detour route comparison
```

This skill is for scenario-level estimation.

## Inputs

Required / primary:

- `cargoQty` — cargo quantity, default unit MT.
- `loadPort`, `dischargePort` — load and discharge ports.
- `freightRate` — freight rate, default USD/MT.
- `bunkerPrice` — bunker price as a single USD/MT, or per grade `{ VLSFO, LSMGO, HSFO }`.
- `speedKn` — speed in kn.
- `portCharges` — port charges, per port or as a total.

Prefer to fill or read from context:

- Per-route `distanceNm` for Suez, Cape, and detour.
- `canalCost` — canal dues (Suez etc.); Cape is usually 0 unless provided.
- `seaConsumptionMtPerDay`, `portConsumptionMtPerDay`.
- `loadPortDays`, `dischargePortDays`, `waitingDays`, `canalDelayDays`.
- `commissionPct`, `freightTaxPct`, `otherVoyageCost`, `hireDay`.
- `demRatePerDay`, `desRatePerDay`, `laytimeDeltaDays`.

When distance is missing, resolve ports then call the **route-by-position** API (below). When consumption, port days, or canal cost are missing, do not invent fixed values — use formula templates or mark “needs input / needs API”.

When bunker price is missing, prefer **`COMMODITY_PRICES_LATEST_TOKEN_API.md`**.

## Port resolution → route distance

### 1) Port names → coordinates

When the user enters load/discharge ports (names only, or coords missing):

1. Call **`SUGGESTION_LOCATION_API.md`**:
   `GET …/ports/suggest/location` with `keyword` = port name (CN or EN).
2. Call **once per port** (separate keywords for load and discharge).
3. **Multiple hits**: for this skill, **temporarily use `data[0]`** as the effective port (`portId`, `lat`, `lon`). Prefer stating which port was auto-selected (name + `portId`).
4. Map coordinates to `{ "lng": lon, "lat": lat }` (also accept `lon`).
5. Empty `data` → ask for another keyword; **never invent** coordinates.

Do **not** use `portguide/getPort/token` for this step.

### 2) Coordinates → voyage distance

With both ends resolved, call **`ROUTEBYPOSITION_TOKEN_SKILL.md`** (not `POST /hifleetrouteapi/getNewRoute`):

```text
GET /routepoints/routebyposition/token
```

Query (see **`ROUTEBYPOSITION_TOKEN_SKILL.md`** for auth and full params):

```text
start=lon,lat          (required)
end=lon,lat            (required)
avoidareaid=optional   (comma-separated avoid-area IDs)
viewpoint=optional     (via-point lon,lat)
```

Normalization:

```text
distanceNm     = waypoints[0].dis  or  nmile
ecaDistanceNm  = waypoints[0].ecadis  (or top-level ecadis if present)
```

Success: `status` is `success` (or equivalent), and at least one of `dis` / `nmile` is a valid number.

Keep `route.requestParams` and raw `route.response` for provenance.

### 3) Use in scenarios

- Single route: one call with load → discharge coords (optional `avoidareaid` / `viewpoint`).
- Suez / Cape / detour comparison: call per scheme with different `avoidareaid` (or omit). If a constraint is unsupported, say so and ask for manual `distanceNm` — never invent nm.
- Common avoid-area IDs (from config / prior responses):

```text
669 Suez Canal
671 Dover Strait
678 Strait of Malacca
696 Taiwan Strait
668 Cape of Good Hope   (often appears in passAvoidArea when routing via Cape)
```

### Flow summary

```text
user names
  → SUGGESTION_LOCATION_API (data[0] if multiple)
  → start/end as lon,lat
  → ROUTEBYPOSITION_TOKEN_SKILL
  → distanceNm / ecaDistanceNm
  → voyage days & cost calc
```

## Calculation order

1. Build route schemes: `suez`, `cape`, `detour`.
2. If a scheme lacks `distanceNm`, resolve ports (suggest/location) then fill distance via route-by-position.
3. For each scheme compute distance, voyage days, fuel cost, port cost, voyage income, voyage cost.
4. Compute TCE.
5. Compute demurrage / despatch sensitivity on the baseline scheme.
6. Output three-route comparison; mark best TCE, shortest voyage, and lowest cash cost.

## Route schemes

Each scheme must include at least:

```text
routeName
distanceNm
speedKn
seaDays
portDays
canalDelayDays
totalVoyageDays
canalCost
fuelCost
portCost
grossFreight
netFreight
voyageCost
tce
```

Definitions:

- **Suez**: Suez-route distance; cost includes `canalCost`; days may include `canalDelayDays`.
- **Cape**: Cape-route distance; usually no Suez canal dues; longer distance and higher fuel.
- **Detour**: user-specified detour distance / days / extra cost; if missing, mark as pending and do not hard-rank against others.

## Core formulas

Voyage days:

```text
seaDays = distanceNm / speedKn / 24
portDays = loadPortDays + dischargePortDays + waitingDays
totalVoyageDays = seaDays + portDays + canalDelayDays
```

Income:

```text
grossFreight = cargoQty * freightRate
commission = grossFreight * commissionPct / 100
freightTax = grossFreight * freightTaxPct / 100
netFreight = grossFreight - commission - freightTax
```

Fuel cost:

```text
seaFuelMt = seaDays * seaConsumptionMtPerDay
portFuelMt = portDays * portConsumptionMtPerDay
fuelCost = sum(fuelMtByType * bunkerPriceByType)
```

If only a single bunker price:

```text
fuelCost = (seaFuelMt + portFuelMt) * bunkerPrice
```

Port cost:

```text
portCost = loadPortCharge + dischargePortCharge + otherPortCharge
```

Voyage cost and TCE:

```text
voyageCost = fuelCost + portCost + canalCost + otherVoyageCost
voyageSurplus = netFreight - voyageCost
tce = voyageSurplus / totalVoyageDays
```

If including time-charter hire:

```text
hireCost = hireDay * totalVoyageDays
profit = voyageSurplus - hireCost
```

## Demurrage / despatch sensitivity

Sensitivity around port-time variance and dem/des rates. Positive = demurrage income; negative = despatch expense.

```text
demurrageIncome = max(laytimeDeltaDays, 0) * demRatePerDay
despatchCost = max(-laytimeDeltaDays, 0) * desRatePerDay
adjustedSurplus = voyageSurplus + demurrageIncome - despatchCost
adjustedDays = totalVoyageDays + max(laytimeDeltaDays, 0)
adjustedTce = adjustedSurplus / adjustedDays
```

Default bands:

```text
-2 days, -1 day, base, +1 day, +2 days
```

Use user bands when provided. Output per band: `daysDelta`, `demDesAmount`, `adjustedSurplus`, `adjustedTce`.

## Output format

Conclusion first, then comparison detail:

```text
Conclusion:
- Best TCE:
- Shortest voyage:
- Lowest cash cost:
- Key risks / missing inputs:

Route comparison:
- Suez: voyage days, fuel cost, port cost, canal dues, TCE
- Cape: voyage days, fuel cost, port cost, canal dues, TCE
- Detour: voyage days, fuel cost, port cost, extra cost, TCE

Demurrage / despatch sensitivity:
- -2 days:
- -1 day:
- base:
- +1 day:
- +2 days:
```

When using a table, columns are fixed:

```text
Route | Distance (nm) | Voyage days | Fuel cost | Port cost | Canal/extra | Net freight | TCE
```

## Self-check

- If `speedKn <= 0`, do not compute sea days; report invalid input.
- If `totalVoyageDays <= 0`, do not compute TCE.
- Prefer distance from **`ROUTEBYPOSITION_TOKEN_SKILL.md`** after port resolve via **`SUGGESTION_LOCATION_API.md`** (`data[0]` when multiple). If the API fails or coords cannot be resolved, mark as pending — do not invent nm.
- Distance, consumption, and canal-cost sources must be traceable; keep route request params and response.
- Suez vs Cape must differ in at least distance, fuel cost, and canal dues.
- Port charges go only into `portCost`, not also into `otherVoyageCost`.
- Demurrage increases surplus; despatch reduces surplus.
- Amounts default to USD; days to 2 decimals; TCE as USD/day.
