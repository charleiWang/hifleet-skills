# 船位 API / Position API

获取（岸基+卫星+移动）船舶最新位置信息。**需配置 usertoken。**

## 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `https://api.hifleet.com/position/position/get/token` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| mmsi | 413829443 | 是 | string | MMSI 号码 |
| usertoken | (从配置读取) | 是 | string | 授权 token |

## 成功响应示例

```json
{
    "result": "ok",
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

## 经纬度换算

- 纬度（度） = `parseFloat(list.la) / 60`
- 经度（度） = `parseFloat(list.lo) / 60`

## 调用流程

1. 检查 token；无则提示并终止。
2. 校验 mmsi（9 位数字字符串）。
3. 请求：`GET .../position/position/get/token?mmsi={mmsi}&usertoken={usertoken}`。
4. 若 `result === "ok"` 解析 list；否则按错误处理。

展示建议包含：船名、MMSI、最后更新时间、经纬度（度）、航速、航向、目的港、状态。
