---
name: ship-position
description: >-
  船位、档案、港口、性能、航程、航线、租船、航运、气象海况、船队、AIS。Use when user asks for vessel position (船位), ship info, port, voyage, route, charter, shipping, weather, fleet, or AIS.
version: 0.1.2
---

# 技能说明

调用 HiFleet API 需配置授权 token。技能列表与触发词见 [references/skills_index.md](references/skills_index.md)。

| 技能 | 状态 | 说明 |
|------|------|------|
| 船位 Ship Position | ✅ 已实现 | 获取最新船舶位置 |
| 档案 Archive | ✅ 已实现 | 船舶/公司档案 |
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

## Token 配置（选填）

1. **环境变量**：`HIFLEET_USER_TOKEN` 或 `HIFLEET_USERTOKEN`
2. **项目/ClawHub 配置**：`usertoken` / `userToken`
3. **请求参数**：接口支持时传入 `usertoken`
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

---

## 安全与合规

本技能仅向 `https://api.hifleet.com` 的船位/档案接口发起只读 GET 请求，token 仅用于 API 鉴权。详见 [SECURITY.md](SECURITY.md)。

## 参考资料与脚本

| 路径 | 说明 |
|------|------|
| [SECURITY.md](SECURITY.md) | 安全说明（网络行为、Token 用途、无动态代码） |
| [references/skills_index.md](references/skills_index.md) | 技能清单（中英双语、触发词） |
| [references/position_api.md](references/position_api.md) | 船位 API 完整说明与响应字段 |
| [references/archive_api.md](references/archive_api.md) | 档案 API 说明与 data 分类 |
| scripts/get_position.py | 按关键字或 MMSI 获取船位（需 token） |
| scripts/get_archive.py | 按 IMO 或 MMSI 获取船舶档案（接口支持 mmsi 参数，内贸船无 IMO 可用 MMSI，需 token） |
