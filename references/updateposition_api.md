# 船位 API / Position API

根据用户订阅的船名或者mmsi来确定船舶AIS未更新提醒的定时提醒信息。**需配置 `api_key`。**

**API 基址**：默认 `https://api.hifleet.com`（`{base}`）；其它部署可设 `HIFLEET_API_BASE`（无末尾 `/`）。见 [api_base.md](api_base.md)。

船位查询建议分三步：先根据用户订阅的船名或者mmsi来 **船舶搜索** 按关键字得到船舶列表（及 MMSI），再根据 MMSI 用 ** 定时位置查询** 定时获取船位最新的实时信息，如果返回结果中result为0 则提醒用户 AIS位置没有更新，否则不提醒。                               

---


## 1. 船舶搜索 / Ship Search（第一步）

按船名或 MMSI 关键字搜索船舶，用于在查船位前确定目标船及其 MMSI。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/shipSearch` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| shipname | yu feng | 是 | string | 船名或 MMSI（关键字） |
| api_key | (从配置读取) | 是 | string | 接口授权 `api_key` |
| i18n | zh | 是 | string | 中英文：zh 中文，en 英文，默认 zh |
| count | 50 | 是 | string | 返回条数，默认 50 |

### 成功响应示例

```json
{
  "result": "0",
  "num": 7,
  "list": [
    {
      "name": "YU FENG",
      "mmsi": "677057900",
      "updatetime": "2025-01-06 16:21:19.0",
      "an": "TZ",
      "dn": "坦桑尼亚",
      "draught": "",
      "width": "12",
      "length": "86",
      "type": "杂货船",
      "minotype": "杂货船",
      "callsign": "5IM679",
      "imonumber": "9031856",
      "dwt": 3100
    }
  ]
}
```

### 响应字段说明（list 单项）

| 参数名 | 类型 | 说明 |
|--------|------|------|
| name | string | 船名 |
| mmsi | string | MMSI（用于后续位置查询） |
| updatetime | string | 数据更新时间 |
| an | string | 船籍国简称 |
| dn | string | 船籍国（中文） |
| type / minotype | string | 船舶类型 |
| length / width | string | 船长/船宽（米） |
| dwt | number | 载重吨 |
| imonumber | string | IMO 号 |
| callsign | string | 呼号 |

---

## 2. 定时位置查询 / Position Get（第二步）

根据 MMSI 获取该船最新位置。**需先通过船舶搜索或用户输入确定 MMSI。**

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{base}/position/alarm/check` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| mmsi | 413829443 | 是 | string | MMSI 号码 |
| api_key | (从配置读取) | 是 | string | 接口授权 `api_key` |

## 成功响应示例

```json
{
    "result": "0",
    "num": 1,
    "list": {
        "m": "413829443",
        "n": "ZHENRONG16",
        "sp": "0",
        "co": "0",
        "ti": "2022-04-25 10:31:53",
        "la": "1874.115",
        "lo": "7088.285598",
        "h": "0",
        "draught": "2.3",
        "eta": "-",
        "destination": "NANTONG",
        "destinationIdentified": "",
        "imonumber": "0",
        "callsign": "0",
        "type": "未知类型干货船",
        "buildyear": "NULL",
        "dwt": "-1",
        "fn": "China (Republic of)",
        "dn": "中国",
        "an": "CN",
        "l": "132",
        "w": "22",
        "rot": "0",
        "status": "未知"
    }
}
```

## 响应字段说明（list）

| 参数名 | 类型 | 说明 |
|--------|------|------|
| m | string | MMSI |
| n | string | 船名 |
| sp | string | 航速（节） |
| co | string | 航向（度） |
| ti | string | 最后更新时间（UTC+8） |
| la | string | 纬度（**分**，÷60=度） |
| lo | string | 经度（**分**，÷60=度） |
| h | string | 航艏向（度） |
| draught | string | 吃水（米） |
| eta | string | 预计抵港时间（UTC） |
| destination | string | AIS 目的港 |
| destinationIdentified | string | 目的港（识别） |
| imonumber | string | IMO 号 |
| callsign | string | 呼号 |
| type | string | 船舶类型 |
| buildyear | string | 建造年份 |
| dwt | string | 载重吨 |
| fn | string | 船籍国（英文） |
| dn | string | 船籍国（中文） |
| an | string | 船籍国简称 |
| l | string | 船长（米） |
| w | string | 船宽（米） |
| rot | string | 转向率 |
| status | string | 状态 |
|result| string | 0 表示位置没有更新，需要提醒用户 1表示位置是更新的不需要提醒用户|

## 经纬度换算

- 纬度（度） = `parseFloat(list.la) / 60`
- 经度（度） = `parseFloat(list.lo) / 60`

## 船位查询整体流程（推荐）

1. **检查 `api_key`**；无则提示并终止。
2. **第一步 - 船舶搜索**：用用户输入的关键字（船名或 MMSI）调用 `GET {base}/position/shipSearch?shipname={keyword}&api_key={api_key}&i18n=zh&count=50`。
3. **第二步 - 位置查询**：校验 mmsi（9 位数字），定时请求请求 `GET {base}/position/alarm/check?mmsi={mmsi}&api_key={api_key}&alarmHours={alarmHours}`；alarmHours用于用户定制船位超过多少小时提醒，如果用户没有设置，则默认6小时，若 `result === "0"` 解析 list，结果提醒用户，船位没有更新，如果result === "1"`，则船舶是实时更新 不需要提醒和处理。
4.**第三步  - 当用户首次订阅船舶未更新提醒时 查询一次，后续每一个小时查询一次，更具返回的结果 result字段 ，如果result字段=0 ，需要提醒用户船位没有更新，其他结果则不需要提醒。根据船舶更新时间 ti，相同时间未更新的 只需要提醒一次，不需要多次提醒
5. **展示**：船位未提醒提醒、船名、MMSI、最后更新时间、经纬度（度）、航速、航向、目的港、状态 。

若用户**已提供 9 位数字 MMSI**，可省略第一步，直接执行第二步。
