# PSC 统计异常 API / PSC statistical anomaly API

查询 **PSC 日批统计异常事件**（表 `psc_anomaly_event`），与「按 IMO 查单船检查记录」的 [psc_api.md](psc_api.md) 互补。**均需**在 Query 中传 `usertoken`（与 `pscapi/get` 相同，技能脚本从 `HIFLEET_USER_TOKEN` / `HIFLEET_USERTOKEN` 读取）。若网关已对路径统一鉴权、应用层暂不解析该参数，多余参数通常可忽略；与 `pscapi/get` 对齐便于同一 token 策略。

**Base URL**：与船位/PSC 一致，默认 `https://api.hifleet.com`。若部署在内网或其它域名，可通过环境变量 `HIFLEET_API_BASE` 覆盖（脚本会读取，**不含**末尾 `/`）。

## 响应包装 HiResult

与 HiFleet 常见接口一致（以实际返回为准）：

| 字段 | 说明 |
|------|------|
| status | 成功多为字符串 `"1"` |
| msg | 如 `SUCCESS` |
| data | 业务载荷：列表接口为 `{ total, page, pageSize, list }`；详情为单条对象；summary 为数组 `[{ severity, cnt }, ...]` |

若返回顶层 `code` 为 **4004/4005/4001** 等，含义与 [psc_api.md](psc_api.md) 中 token/权限说明类似（以服务端为准）。

---

## 1. 分页列表

| 项目 | 值 |
|------|-----|
| URL | `{BASE}/pscapi/openclaw/anomalies` |
| 方法 | GET |

### Query 参数

| 参数 | 必选 | 说明 |
|------|------|------|
| usertoken | 是 | 授权 token |
| dateFrom | 否 | `yyyy-MM-dd`；与 `dateTo` 都省略时服务端默认最近约 30 天 |
| dateTo | 否 | `yyyy-MM-dd` |
| authority | 否 | 检查当局，精确匹配 |
| flag | 否 | 船旗国，精确匹配 |
| port | 否 | 港口，精确匹配 |
| severity | 否 | 如 `HIGH` / `MEDIUM` / `LOW` |
| anomalyType | 否 | 如 `DETENTION_RATE_SPIKE`、`AVG_DEFECTS_SPIKE` |
| sliceType | 否 | 如 `AUTHORITY_FLAG_PORT_TYPE` |
| metric | 否 | 如 `detention_rate`、`avg_defects` |
| status | 否 | 如 `open` |
| page | 否 | 默认 `1` |
| pageSize | 否 | 默认 `20`，最大 `100` |

### data 结构（成功时）

- `total`：总条数  
- `page`、`pageSize`  
- `list`：事件数组，常见字段含 `id`、`title`、`dateStart`、`dateEnd`、`severity`、`metric`、`currentValue`、`baseline`、`changeRate`、`description`、`evidence`（多为 JSON 字符串）等。

---

## 2. 按严重级别汇总

| 项目 | 值 |
|------|-----|
| URL | `{BASE}/pscapi/openclaw/anomalies/summary` |
| 方法 | GET |

### Query 参数

与列表相同筛选：`usertoken` 必填；`dateFrom`、`dateTo`、`authority`、`flag`、`port`、`severity`、`anomalyType`、`sliceType`、`metric`、`status` 可选（日期默认逻辑同列表）。

### data 结构

数组，元素示例：`{ "severity": "HIGH", "cnt": 12 }`。

---

## 3. 单条详情

| 项目 | 值 |
|------|-----|
| URL | `{BASE}/pscapi/openclaw/anomalies/{id}` |
| 方法 | GET |

### Query 参数

| 参数 | 必选 |
|------|------|
| usertoken | 是 |

路径 `{id}` 为事件主键（数字）。

失败时可能返回 `status` 非 1 或业务错误文案（如记录不存在）。

---

## OpenClaw 调用建议

1. 先 **summary** 回答「最近严重异常有多少」；再按需 **list** 拉页；用户追问某条时用 **get {id}** 展开 `evidence`。  
2. `list` 为空时说明可能检测阈值较严或尚未跑全量异常补算，可提示用户放宽 newpsc 中 `psc.stats` 或执行 `backfill-anomalies`（见运维文档）。  
3. `authority`/`flag`/`port` 须与入库字符串**一致**（精确匹配）；自然语言需先做别名映射或由用户确认拼写。

---

## 脚本

`scripts/get_psc_anomalies.py`：`list` / `summary` / get `<id>`，从环境变量读 token 与可选 `HIFLEET_API_BASE`。
