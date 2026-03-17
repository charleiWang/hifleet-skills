# 海峡通航 API / Strait Traffic API

红海与波斯湾相关海峡的船舶通航情况查询。**完整请求 URL、参数名与响应格式请以 ShowDoc 为准**：[http://showdoc.hifleet.com/web/#/45/2234](http://showdoc.hifleet.com/web/#/45/2234)。

## 支持的海峡（oid）

| 海峡名称     | oid    | 英文/备注   |
|--------------|--------|-------------|
| 曼德海峡     | 24480  | Bab el-Mandeb |
| 苏伊士运河   | 132808 | Suez Canal  |
| 好望角       | 1062830| Cape of Good Hope |
| 霍尔木兹海峡 | 24471  | Strait of Hormuz |

## 鉴权与时间范围

- **无 usertoken**：仅可查询**最近 1 周**内的时间区间；超出则需鉴权。
- **有 usertoken**：时间区间不限，可查任意起止时间。

## 请求约定（以 ShowDoc 为准）

- 请求 URL：见 ShowDoc 文档；脚本中暂用占位 `https://api.hifleet.com/traffic/strait`，若文档不同请改脚本中的 `STRAIT_TRAFFIC_URL` 及参数名。
- 请求方式：一般为 **GET**（以文档为准）。
- 常见参数（名称以文档为准）：
  - **oid**：海峡 ID，见上表。
  - **startTime** / **endTime**（或 start、end）：时间区间，格式以文档为准（如 `yyyy-MM-dd` 或时间戳）。
  - **usertoken**：可选；传入时时间范围不限。

## 调用流程

1. 确定海峡：用户指定海峡名称或 oid，映射到上表 oid。
2. 确定时间区间：若用户未指定，无 token 时默认最近 7 天；有 token 时可按用户指定或默认最近 7 天。
3. **无 token 时**：校验 endTime - startTime ≤ 7 天，否则提示“仅支持最近 1 周，或配置 usertoken 后查询更长时间”。
4. 请求接口：GET，传入 oid、startTime、endTime，有 token 时传入 usertoken。
5. 解析响应并展示通航情况（字段以 ShowDoc 响应示例为准）。
