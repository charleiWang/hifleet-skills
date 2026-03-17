# 区域船舶 API / Area Traffic API

查询指定区域内的当前船舶列表。**需配置 usertoken。**

## 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `https://api.hifleet.com/position/gettraffic/token` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| usertoken | (从配置读取) | 是 | string | 授权 token |
| bbox | 120,15,121,17 | 否 | string | 矩形区域：左下角经度、左下角纬度、右上角经度、右上角纬度（逗号分隔） |
| polygon | POLYGON((...)) | 否 | string | WKT 格式多边形，如 POLYGON((lon1 lat1,lon2 lat2,...))，待接口更新后支持 |

**bbox 与 polygon 二选一**（当前以 bbox 为主；polygon 待接口支持后使用）。

## 成功响应

- `result`: "ok"
- `num`: 数量
- `list`: 船舶列表，每项字段见下

### list 单项字段说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| name | string | 船名 |
| lon | number | 经度（度） |
| lat | number | 纬度（度） |
| mmsi | string | MMSI |
| heading | string | 航艏向（度） |
| speed | string | 航速（节） |
| updatetime | string | 最后更新时间（UTC+8） |
| an | string | 船籍简称 |
| dn | string | 船籍中文 |
| eta | string | 预计抵港时间（UTC） |
| draught | string | 吃水（米） |
| destination | string | 目的港 |
| width | string | 船宽（米） |
| length | string | 船长（米） |
| type | string | 船舶类型 |
| minotype | string | 档案船舶类型 |
| callsign | string | 呼号 |
| imonumber | string | IMO |
| course | string | 航向 |
| turnrate | string | 转向率 |
| status | string | 状态 |
| fn | string | 船籍国 |
| dwt | string | 载重吨 |

## 调用流程

1. 检查 token；无则提示并终止。
2. 确定区域：用户提供矩形（西/南/东/北 或 左下经度、左下纬度、右上经度、右上纬度）或后续支持的 polygon。
3. 请求：`GET .../position/gettraffic/token?bbox={minLon},{minLat},{maxLon},{maxLat}&usertoken={usertoken}`。
4. 若 `result === "ok"` 解析 list，按需展示船名、MMSI、经纬度、航速、状态、目的港等。
