# 船货盘富化与距离排序接口（路由 A · 邮件 SQLite）

本文件为 **hifleet-mytonnages** 中 **路由 A** 在 **2.4.1 写入 SQLite 之后** 的**数据富化**与**按距离排序查询**约定；**路由 B（班轮船期）不适用本文**。

---

## 分发模式

1. 船舶档案、港口 ID、港间距离由 **HiFleet `api.hifleet.com`** 提供；助手在环境中发 **HTTPS** 请求，**不得**臆造 IMO 档案字段或 `portid`。  
2. 密钥与路由 B 相同：`hifleet_api_key`（`config.json`）或 `HIFLEET_API_KEY`（环境变量）；各接口 Query 参数 **`api_key`** = 该串，**勿在对话中完整暴露**。  
3. **写入顺序（硬性）**：邮件 **2.4** 解析 → **2.4.1** `charter_facts_tool.py save` 落库 → **2.4.2** 按本文批量富化并 **UPDATE** 同行 → 之后 **2.3 / 2.5** 检索与筛选。未富化行可展示邮件字段，但**距离排序查询**须先完成 **§3** 所需 `portid` 富化。

---

## 配置与根路径

| 含义 | 默认值 |
|------|--------|
| 租船/船货盘 API 根（无末尾 `/`） | `https://api.hifleet.com/openclaw/vessel/charter` |

**根路径**：`hifleet_charter_api_base`（config）→ `HIFLEET_CHARTER_API_BASE`（环境）→ 上表。  
无有效 **`hifleet_api_key`** 时：**不得**调本文接口；可仅基于邮件解析字段回答，并提示用户配置 Key（见 `CONFIG.example.md`）。

---

## 1. 船舶档案批量查询（按 IMO 补充船盘）

**`POST {root}/ship-archive/batch?api_key={密钥}`**

- **方法**：**POST**（**禁止 GET**，现网对 GET 返回 method not supported）。  
- **Header**：`Content-Type: application/json`  
- **Body**：

```json
{
  "imos": ["1000174", "1000265"]
}
```

- **IMO 来源**：`openvessel_plate` 行上邮件解析的 **`IMO`** 列；去重、去空、仅数字串；无 IMO 的行**跳过**本接口。  
- **成功**（`status` 为 `"1"`、`msg` 为 `SUCCESS`）：`data.list[]` 每项含 `ShipName`、`imo`、`callsign`、`YearOfBuild`、`dwt`、`flagname`、`flagcode`、`Length`、`width`、`draught`、`GrossTonnage`、`Shipbuilder`、`type`、`registeredOwner`、`operator`、`shipManager`、`minotype` 等。  
- **落库**：按 **`imo`** 匹配 `openvessel_plate` 行，将档案字段写入 **`ship_archive_json`**（完整 JSON 备份），并同步写入分列（见 **`WORKFLOW_2_MAIL.md` §2.4.2**）：`档案_船名`、`档案_呼号`、`档案_建造年`、`档案_dwt`、`档案_船旗`、`档案_船长`、`档案_船宽`、`档案_吃水`、`档案_总吨`、`档案_造船厂`、`档案_船型`、`档案_船东`、`档案_经营人`、`档案_管理公司`、`档案_细分船型`。邮件已有同义字段且档案非空时，**以档案 API 为准覆盖**对应展示列（如 `载重吨`、`建造年份`、`船型`）。  
- **失败**：单批 IMO 失败时记录错误、**不**伪造档案；其余行继续。

---

## 2. 港口 ID 解析（OPEN / 装货港 / 卸货港）

**`POST {root}/port/portid?api_key={密钥}`**

- **Header**：`Content-Type: application/json`  
- **Body**：

```json
{
  "portname": "Singapore+tianjin"
}
```

- **`portname` 规则**：与邮件解析一致，**多港用 `+` 连接**（与 `SKILL.md` Notes 相同）；船盘取 **`OPEN位置`**；货盘装港取 **`装货港`**、卸港取 **`卸货港`**（有则拼入或分次请求，以一次 `+` 批量为准）。  
- **成功**：`data.portid` 为逗号分隔 ID 串（如 `"15843,22214"`），与输入港序对应；`data.ok` 为 `true` 时写入库。  
- **落库**：  
  - **`openvessel_plate`**：`OPEN位置` → 列 **`portid`**（存完整 `portid` 串）。  
  - **`cargo_plate`**：`装货港` → **`portid`**；`卸货港` → **`discharging_portid`**。  
- **幂等**：同一 `message_id`+`row_index` 再次富化时 **UPDATE** 覆盖 `portid` / `discharging_portid`。  
- **失败**：`portid` 留空，距离排序时该行**不参与**排序或排在末尾，并可在输出中标注「港口未解析」。

---

## 3. 船盘/货盘按距离排序查询

用户输入**查询港口**（如「新加坡附近 open 的船」「离天津最近的船盘」）时，在 **2.3** SQLite 初筛之后、**2.5** 展示之前，**默认按距离升序**排序（除非用户明确要求仅按邮件时间）。

### 3.1 解析查询港 `queryPortid`

对**用户指定的查询港口**调用 **§2**（`portname` 为单港或多港 `+` 拼接），取返回的 **`portid`**。多 ID 时取**第一个**作为 `queryPortid`，或以业务约定取主港 ID（须在当次回复中说明采用了哪一段 ID）。

### 3.2 筛选候选行

- **船盘**：`openvessel_plate` 中 `OPEN位置` / `portid` 与用户关心区域相关的行（SQLite `LIKE` 或 `portid` 非空）。  
- **货盘**：`cargo_plate` 中 `装货港` / `portid` 等匹配用户条件的行。  
- 用户明确「open 在 X 港」时，可先用 `OPEN位置` / `装货港` **LIKE** 缩小集合，再算距离。

### 3.3 批量港距

**`POST {root}/port-distances/batch?api_key={密钥}`**

- **Body**：

```json
{
  "queryPortid": "27999",
  "indexData": [
    { "index": "281951", "portid": "15843" },
    { "index": "281949", "portid": "215881,15843" }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `queryPortid` | §3.1 得到的查询港 ID |
| `indexData[].index` | 候选行**稳定主键**字符串：推荐 `sqlite` 自增 `id`，或 `{message_id}:{row_index}:{cargo\|openvessel}` |
| `indexData[].portid` | 该行 **`portid`**（OPEN 或装货港解析结果；多港逗号串原样传入） |

- **成功**：`data.list[]` 含 `index`、`dist`（海里或接口约定单位）、`nearestPortId`、`portid` 等。  
- **排序**：按 **`dist` 升序**；`dist` 缺失的排最后。  
- **展示**：每条船盘/货盘输出中**须含**「距查询港约 **{dist}**」（单位与接口一致）；仍遵守 **`WORKFLOW_OUTPUT.md`** 固定链接。  
- **批量**：单次 `indexData` 过多时可分批请求，合并后统一排序。

---

## 错误与鉴权

- `status` 非成功或 HTTP 4xx/5xx：检查 `api_key`、Body 格式、**POST 方法**。  
- 积分/鉴权类错误：提示用户在 HiFleet 网站检查密钥与余额，**勿**伪造 `portid` 或档案字段。

---

## 与 `charter_facts_tool.py` 的衔接

- **落库 / 检索**：`save`、`search`（见 **`WORKFLOW_2_MAIL.md` §2.4.1**）。  
- **富化回写**：`python scripts/charter_facts_tool.py enrich [--db …]`（拉取 §1、§2 并 UPDATE；须已配置 `hifleet_api_key`）。  
- **按港距排序查询**：`python scripts/charter_facts_tool.py query-by-port --port "Singapore" [--db …] [--limit 50]`（内部 §2 + §3；输出 JSON 已按 `dist` 排序）。

当前宿主环境以允许的方式调用；**勿**要求零基础用户自行拼 curl。
