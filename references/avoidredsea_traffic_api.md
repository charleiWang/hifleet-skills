# 集装箱红海饶航 API / AvoidRedsea Traffic API（集装箱红海绕航船舶统计）
集装箱饶航红海船舶统计。

方向定义

| 方向 | 含义 | 说明 |
|------|------|------|
| 东 | 向东 | 船舶由西向东航行 |
| 西 | 向西 | 船舶由西向东航行 |

## 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `http://112.126.23.236:8234//routerisk//getAvoidRedSeaDetail/token` |
| 请求方式 | **POST** |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| startdate | 2024-01-17 | 是 | string | 开始日期，格式 yyyy-MM-dd |
| enddate | 2024-01-17 | 是 | string | 结束日期，格式 yyyy-MM-dd |
| i18n | en | 否 | string | 输出语言，zh 或 en，默认 zh |
| usertoken | (从配置读取) | 否 | string | 授权 token；**无 usertoken 仅可查最近 1 周**，有 usertoken 时间区间不限 |
| usertoken | (从配置读取) | 否 | string | 授权 token；**无 token 仅可查最近 1 周**，有 token 时间区间不限 |


## 成功响应结构


- **status** 数据返回状态1成功0失败
- **data**：数组，获取查询时间段内的所有船舶
  - **updatetime**：时间
  - **mmsi**：船舶mmsi
  - **name**：船舶名称
  - **areaname**：方向：向西或者向东
     
## 鉴权与时间范围

- **无 usertoken**：仅可查询**最近 1 天**内的时间区间；超出则接口可能报错或需鉴权。
- **有 usertoken**：时间区间不限，可查任意起止时间。

## 调用流程

1确定时间区间：starttime、endtime，格式 yyyy-MM-dd。**无 token 时**校验区间 ≤ 1 天。
2**POST** 请求：`.../routerisk/getAvoidRedSeaDetail/token?starttime={starttime}&endtime={endtime}&i18n={zh|en}[&usertoken=...]`，有 token 时传入 usertoken。
3解析响应：data 下按 areaname / updatetime 展示绕航方向、总艘次及船舶列表。
