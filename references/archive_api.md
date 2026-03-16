# 船舶档案 API / Ship Archive API

根据 IMO 号获取船舶档案（含基本信息、尺度、舱容、建造、入级、动力、公司信息、互保协会等）。需配置 usertoken。

## 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `https://api.hifleet.com/shiparchive/getShipArchiveWithEnginAndCompany` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| usertoken | (从配置读取) | 是 | string | 授权 token |
| imo | 1000112 | 是 | string | IMO 号（7 位数字） |

## 成功响应

- `status`: "1" 表示成功
- `msg`: "success"
- `data`: 数组，每项为一大类，含 `key`、`labelZh`、`labelEn`、`value`

### data 项结构

- **value** 可为「键值列表」或「嵌套结构」：
  - 键值列表：`value` 为数组，元素为 `{ key, value, labelZh, labelEn, valueZh, valueEn }`
  - 嵌套结构：`value` 为数组，元素内仍有 `value` 数组（如 MMSI 变更记录、入级记录、公司信息、船舶动力等）

### 常见 data 分类（key）

| key | labelZh | 说明 |
|-----|---------|------|
| basicInfo | 基本信息 | IMO、MMSI、船名、曾用船名、呼号、类型、船旗、船籍港、营运状态、航速、交付日期等 |
| particularInfo | 船舶尺度 | 船长、船宽、型深、吃水、总长、两柱间长等 |
| shipMmsiHistoryInfo | MMSI变更记录 | 呼号/MMSI/生效日期历史 |
| shipCapacityInfo | 船舶舱容 | 载重吨、总吨、净吨、舱容、箱位量等 |
| shipConstructionInfo | 建造信息 | 建造国、建造日期、船厂 |
| shipClassSocietyInfo | 入级记录 | 船级社、入级标识、生效日期 |
| shipPowerInfo | 船舶动力 | 主机设计商/制造商/型号、功率等 |
| managementInfo | 公司信息 | 受益船东、注册船东、管理公司、经营公司、技术管理公司（名称、地址、电话、Email、网址） |
| shipPandIClub | 互保协会 | P&I 协会 |

## 调用流程

1. 检查 token；无则提示并终止。
2. 校验 imo（一般为 7 位数字，或 IMO 前缀+7 位）。
3. 请求：`GET .../shiparchive/getShipArchiveWithEnginAndCompany?imo={imo}&usertoken={usertoken}`。
4. 若 `status === "1"` 解析 data，按 labelZh 分块展示，字段值优先用 valueZh。

若用户只提供船名或 MMSI，可先调用 `position/shipSearch` 得到船舶列表，取其中的 `imonumber` 再调本接口。
