---
name: ship-position
description: >-
  船位、档案、区域船舶、红海波斯湾海峡通航、港口、性能、航程、航线、租船、航运、气象海况、船队、AIS。Use when user asks for vessel position (船位), ship info, area traffic (区域船舶 范围内船舶), strait traffic (红海 波斯湾 曼德 苏伊士 好望角 霍尔木兹), port, voyage, route, charter, shipping, weather, fleet, or AIS.
version: 0.1.7
# 可选：仅部分接口需要鉴权，配置后船位/档案等能力可用；不配置也可使用不需鉴权的部分
optionalEnv:
  - HIFLEET_USER_TOKEN
  - HIFLEET_USERTOKEN
# 来源与联系（便于安全审核）
homepage: https://www.hifleet.com
source: https://api.hifleet.com
---

# 技能说明

不配置鉴权也可使用本技能中不需 token 的部分；**船位、档案等已实现功能需配置 token 后可用**。技能列表与触发词见 [references/skills_index.md](references/skills_index.md)。

| 技能 | 状态 | 说明 |
|------|------|------|
| 船位 Ship Position | ✅ 已实现 | 获取最新船舶位置 |
| 档案 Archive | ✅ 已实现 | 船舶/公司档案 |
| 红海/波斯湾通航 Strait Traffic | ✅ 已实现 | 海峡通航统计（曼德、苏伊士、好望角、霍尔木兹），POST；无 token 限最近 1 周，有 token 不限 |
| 区域船舶 Area Traffic | ✅ 已实现 | 查询指定区域内的当前船舶：支持 bbox、areaId（区域清单 id）或 polygon（WKT），需 token |
| 港口 Port | 待实现 | 港口、泊位、锚地 |
| 性能 Performance | 待实现 | 油耗、能效、主机性能 |
| 航程 Voyage | 待实现 | 航次、挂港、ETA/ETD |
| 航线 Route | 待实现 | 推荐航线、航路点 |
| 租船 Charter | 待实现 | 租约、租家、租金 |
| 航运 Shipping | 待实现 | 运价、市场、新闻 |
| 气象海况 Weather | 待实现 | 风浪、台风、能见度 |
| 船队 Fleet | 待实现 | 多船监控、船队报表 |
| AIS | 待实现 | AIS 报文、轨迹回放 |

---

## Token 配置（可选，部分接口必填）

船位、档案等已实现功能依赖 HiFleet API 鉴权；**不配置 token 时这些接口不可用，但技能中其他不需鉴权的部分仍可使用**。需要用到船位/档案时，请配置：

1. **环境变量**（二选一）：`HIFLEET_USER_TOKEN` 或 `HIFLEET_USERTOKEN`
2. **项目/ClawHub 配置**：`usertoken` / `userToken`
3. **请求参数**：接口支持时传入 `usertoken`

建议使用仅限本技能使用的专用 token，停用后及时轮换。

## 常用定义

国际航行船舶 : 通常有有效的IMO注册号码的船舶
电子围栏: 区域范围

---

## 已实现功能

### 船位 / Ship Position

获取（岸基+卫星+移动）船舶最新位置信息。支持**关键字（船名或 MMSI）**查询，自动走“先搜船、再查位”的两步流程。

- **触发**：船位、位置、报位、在哪、MMSI、ship position、vessel position
- **输入**：关键字（船名或 MMSI）或直接 9 位 MMSI；usertoken 从配置读取
- **API 详情**：[references/position_api.md](references/position_api.md)（含 shipSearch 与 position/get/token）
- **脚本**：`scripts/get_position.py`（支持关键字或 MMSI，可选用于命令行/集成）

**两步流程**：

1. **第一步 - 搜船**：用用户关键字调用 `position/shipSearch`（shipname、usertoken、i18n=zh、count）。
2. **第二步 - 查位**：根据结果数量处理：
   - **0 条**：提示未找到，请检查关键字。
   - **1 条**：直接取该条 `mmsi`，调用 `position/position/get/token` 查位置并展示。
   - **多条**：若可推断用户目标船（如关键字为完整 MMSI 或唯一匹配船名），则用对应 MMSI 查位；否则列出船名/MMSI/船型/船籍等，**请用户选择具体 MMSI**，再按所选 MMSI 调用 `position/position/get/token` 查位置。

若用户已提供 **9 位数字 MMSI**，可省略第一步，直接调用 `position/position/get/token`。展示时经纬度需将接口返回的 la/lo 除以 60 转为度。

### 档案 / Archive

根据 IMO 或 MMSI 获取船舶档案（基本信息、尺度、舱容、建造、入级、动力、公司信息、互保协会等）。接口支持 **imo 与 mmsi 二选一**，**内贸船无 IMO 时仅传 mmsi 即可**。船名不支持，需先通过 shipSearch 得到 MMSI/IMO。

- **触发**：档案、船舶信息、船籍、船型、船东、管理公司、archive、vessel profile、ship info
- **输入**：IMO（7 位）或 MMSI（9 位）；usertoken 从配置读取
- **API 详情**：[references/archive_api.md](references/archive_api.md)
- **脚本**：`scripts/get_archive.py`（支持 IMO 或 MMSI，MMSI 直接传 mmsi 参数，需 token）

**调用流程**：检查 token → 若为 **IMO**：GET `...?imo={imo}&usertoken=...`；若为 **MMSI**：GET `...?mmsi={mmsi}&usertoken=...`（支持内贸船无 IMO）→ 解析 data，按 labelZh 分块展示。船名需先 shipSearch 得到 MMSI/IMO 再查档案。

### 红海与波斯湾海峡通航 / Strait Traffic

咽喉航道通航船舶统计，支持曼德海峡、苏伊士运河、好望角、霍尔木兹海峡，按日期区间与方向返回船型统计及船舶明细。**无 usertoken 仅可查最近 1 周，有 usertoken 时间区间不限**。

- **触发**：红海、波斯湾、海峡通航、曼德海峡、苏伊士运河、好望角、霍尔木兹、strait traffic、Red Sea、Persian Gulf
- **输入**：海峡名称或 oid；可选开始/结束日期（yyyy-MM-dd），不传默认最近 7 天；可选 i18n（zh/en）。usertoken 从配置读取，有则时间不限。
- **API 文档**：[references/strait_traffic_api.md](references/strait_traffic_api.md)；完整接口以 [ShowDoc 45/2234](http://showdoc.hifleet.com/web/#/45/2234) 为准。
- **脚本**：`scripts/get_strait_traffic.py`（海峡名或 oid + 可选 startdate/enddate/i18n，有 token 可查超 7 天）

**接口**：**POST** `http://api.hifleet.com/position/statisticzonetraffic`，Query 参数 oid、startdate、enddate、i18n（可选）、usertoken（可选）。**海峡 oid**：曼德海峡 24480、苏伊士运河 132808、好望角 1062830、霍尔木兹海峡 24471。无 token 时校验时间区间 ≤ 7 天。

### 区域船舶 / Area Traffic

查询当前指定区域内的船舶列表。支持三种区域指定方式：**矩形 bbox**、**区域 id（areaId）** 或 **WKT 多边形（polygon）**。用户仅文字描述区域（如 [波斯湾]「红海」「北太平洋」「马六甲海峡」）时，先查区域清单再按 areaId 查询。

- **触发**：区域船舶、范围内船舶、区域船位、某区域有多少船、area traffic、vessels in area
- **输入**：① 矩形区域（左下经度、左下纬度、右上经度、右上纬度）；或 ② 区域名称/海区/贸易区（先调区域清单接口，用 name/cnName 匹配得到 id，再按 areaId 查）；或 ③ WKT 格式 polygon；usertoken 必填
- **API 详情**：[references/area_traffic_api.md](references/area_traffic_api.md)（gettraffic 支持 bbox、areaId、polygon）；[references/areas_api.md](references/areas_api.md)（区域清单）
- **脚本**：`scripts/get_areas.py`（获取区域清单，供按名称选区域）；`scripts/get_area_traffic.py`（bbox 四参数、`--area-id <id>` 或 `--polygon "POLYGON((...))"`，需 token）

**调用流程**：检查 token → 若用户给的是**矩形坐标**：组 bbox → GET `position/gettraffic/token?bbox=...&usertoken=...`；若用户给的是**文字描述**：GET `position/areas/token`（可选 usertoken）→ 用 name/cnName 匹配得 id → GET `position/gettraffic/token?areaId={id}&usertoken=...`；若用户给的是**WKT 多边形**：GET `position/gettraffic/token?polygon=...&usertoken=...` → 解析 list 展示船名、MMSI、经纬度、航速、状态、目的港等。

---

## 安全与合规

本技能仅向 api.hifleet.com 的船位/档案/海峡通航/区域船舶等接口发起只读请求（GET 或 POST）；海峡通航统计无需 token，其余需鉴权的接口使用 token。详见 [SECURITY.md](SECURITY.md)。

## 参考资料与脚本

| 路径 | 说明 |
|------|------|
| [SECURITY.md](SECURITY.md) | 安全说明（网络行为、Token 用途、无动态代码） |
| [references/skills_index.md](references/skills_index.md) | 技能清单（中英双语、触发词） |
| [references/position_api.md](references/position_api.md) | 船位 API 完整说明与响应字段 |
| [references/archive_api.md](references/archive_api.md) | 档案 API 说明与 data 分类 |
| [references/strait_traffic_api.md](references/strait_traffic_api.md) | 红海/波斯湾海峡通航 API（oid、时间范围、ShowDoc 链接） |
| [references/area_traffic_api.md](references/area_traffic_api.md) | 区域船舶 API（bbox、areaId、polygon、usertoken） |
| [references/areas_api.md](references/areas_api.md) | 区域清单 API（海区/贸易区列表，供按名称选 areaId） |
| scripts/get_position.py | 按关键字或 MMSI 获取船位（需 token） |
| scripts/get_archive.py | 按 IMO 或 MMSI 获取船舶档案（接口支持 mmsi 参数，内贸船无 IMO 可用 MMSI，需 token） |
| scripts/get_strait_traffic.py | 海峡通航统计（POST statisticzonetraffic），oid+日期+i18n；无 token 限 7 天，有 token 不限 |
| scripts/get_areas.py | 区域清单（海区/贸易区），供按名称匹配 areaId |
| scripts/get_area_traffic.py | 区域船舶（bbox、--area-id 或 --polygon，需 token） |
