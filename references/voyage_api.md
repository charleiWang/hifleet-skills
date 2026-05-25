# 航程 API / Voyage API（OpenClaw）

单船挂靠、航次、上一离港及当前停船。**需配置 `api_key`。** 用户仅给船名/关键字时，先调 `position/shipSearch` 取得 MMSI（见 [position_api.md](position_api.md)）。

**API 基址**：默认 `https://api.hifleet.com`（`{base}`）；其它部署可设 `HIFLEET_API_BASE`（无末尾 `/`）。见 [api_base.md](api_base.md)。

---

## 能力一览

| 能力 | capabilityCode | 路径 | 方法 | 计费 |
|------|----------------|------|------|------|
| 历史挂靠 | `vessel.portcalls.history` | `/position/getcallport/token` | GET / POST | RESULT_COUNT：每 20 条 1 点，最低 2 点 |
| 历史航次（简版） | `vessel.voyage.history` | `/position/getvoyagelist/token` | GET / POST | RESULT_COUNT：每 20 条 1 点，最低 2 点 |
| 历史航次（详版） | `vessel.voyage.history` | `/portofcall/getvoyages` | GET / POST | RESULT_COUNT：每 20 条 1 点，最低 2 点 |
| 上一港 | `vessel.departure.last` | `/position/lastdeparture/token` | GET / POST | FIXED |
| 当前停船 | `vessel.stop.current` | `/position/getstop/token` | GET / POST | FIXED |

---

## 1. 历史挂靠 / Port call history

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/getcallport/token` |
| 请求方式 | `GET` 或 `POST` |

### Query 参数

| 参数名 | 必选 | 说明 |
|--------|------|------|
| mmsi | 是 | 9 位 MMSI |
| starttime | 是 | 开始时间（北京时间），如 `2019-01-01 00:00:00` |
| endtime | 是 | 结束时间（北京时间） |
| accuracyval | 否 | 挂靠识别精度，默认 `6` |
| api_key | 是 | 接口授权 |

### 响应要点

- 成功：`result=ok`，`num` 为条数，`list.shipRouteFeature[]` 按时间**降序**（最新在前）
- 单条字段：`mPortname`、`cnportname`、`portcode`、`mUpdatetime`（挂靠/到港时间）、`mleavetime`（离港时间）、`country`、`countryCnName`、`lat`、`lon`、`fre`（近一年该港挂靠次数）

---

## 2. 历史航次（简版）/ Voyage list (default window)

默认返回约最近 10 个月航次，仅传 MMSI。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/getvoyagelist/token` |
| 请求方式 | `GET` 或 `POST` |

### Query 参数

| 参数名 | 必选 | 说明 |
|--------|------|------|
| mmsi | 是 | 9 位 MMSI |
| api_key | 是 | 接口授权 |

### 响应要点

- 成功：`result=ok`，`list.voyage[]` 含 `startport`/`endport`、`startportcode`/`endportcode`、`starttime`/`endtime`、`timelong`（航行小时数）

---

## 3. 历史航次（详版）/ Voyages with time range

指定时间区间，返回含航程、航速、吃水等明细的航次列表。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/portofcall/getvoyages` |
| 请求方式 | `GET` 或 `POST` |

### Query 参数

| 参数名 | 必选 | 说明 |
|--------|------|------|
| mmsi | 是 | 9 位 MMSI |
| starttime | 是 | 开始时间（北京时间） |
| endtime | 是 | 结束时间（北京时间） |
| accuracyval | 否 | 默认 `5` |
| updatedistance | 否 | 是否补算航程距离，默认 `1` |
| api_key | 是 | 接口授权 |

### 响应要点

- 成功：`result=OK`，`list[]` 为航次对象数组
- 主要字段：`startport`/`endport` 及中英文港名、国家、`starttime`/`endtime`、`timelong`、`voyage`（航程海里）、`maxspeed`/`mediumspeed`、吃水等

---

## 4. 上一港 / Last departure

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/lastdeparture/token` |
| 请求方式 | `GET` 或 `POST` |

### Query 参数

| 参数名 | 必选 | 说明 |
|--------|------|------|
| mmsi | 是 | 9 位 MMSI |
| api_key | 是 | 接口授权 |

### 响应要点

- 成功：`result=ok`，`list` 为单条对象：`portcode`、`portname`、`departtime`（北京时间）、`country`、`countryCode`

---

## 5. 当前停船 / Current stop

与 legacy `/portofcall/get/shipstoppedplaceandtime` 语义一致。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/getstop/token` |
| 请求方式 | `GET` 或 `POST` |

### Query 参数

| 参数名 | 必选 | 说明 |
|--------|------|------|
| mmsi | 是 | MMSI |
| api_key | 是 | 接口授权 |

### 响应要点

- 成功：`message=ok`，`data[]` 含 `portcode`、`enportname`、`cnportname`、`encountry`、`cncountry`、`countrycode`、`lat`、`lon`、`stoptime`、`starttime`、`accumulatetime`

---

## Agent 路由建议

| 用户意图 | 优先接口 |
|----------|-----------|
| 某时段挂靠/靠港记录 | `getcallport/token` |
| 最近航次、不需自定义时间 | `getvoyagelist/token` |
| 指定区间、要航程/航速明细 | `portofcall/getvoyages` |
| 上次从哪离港 | `lastdeparture/token` |
| 现在停在哪、停多久 | `getstop/token` |
