---
name: ship-position
description: >-
  HiFleet Claw 应用技能：船位、档案、港口、性能、航程、航线、租船、航运、气象海况、船队、AIS。
  Use when user asks for vessel position (船位), ship info, port, voyage, route, charter, shipping, weather, fleet, or AIS.
---

# HiFleet Claw 应用技能

HiFleet Claw 提供船位、档案、港口、性能、航程、航线、租船、航运、气象海况、船队、AIS 等技能。**所有调用 HiFleet API 的功能均需配置授权 token 后才可使用。**

## 技能清单

完整技能列表与触发词见 [references/skills_index.md](references/skills_index.md)。

| 技能 | 状态 | 说明 |
|------|------|------|
| 船位 Ship Position | ✅ 已实现 | 获取最新船舶位置 |
| 档案 Archive | 待实现 | 船舶/公司档案 |
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

获取（岸基+卫星+移动）船舶最新位置信息。

- **触发**：船位、位置、报位、MMSI、ship position、vessel position
- **输入**：MMSI（必填）、usertoken（从配置读取）
- **API 详情**：[references/position_api.md](references/position_api.md)
- **脚本**：`scripts/get_position.py`（可选，用于命令行或集成调用）

**调用流程**：检查 token → 校验 MMSI → GET 位置 API → 解析并展示（经纬度需将 la/lo 除以 60 转为度）。

---

## 参考资料与脚本

| 路径 | 说明 |
|------|------|
| [references/skills_index.md](references/skills_index.md) | 技能清单（中英双语、触发词） |
| [references/position_api.md](references/position_api.md) | 船位 API 完整说明与响应字段 |
| scripts/get_position.py | 按 MMSI 获取最新船位（需配置 token） |
