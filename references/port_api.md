# 港口指南 API / Port guide API

港口列表检索与单港详情。**需配置 usertoken**（与其它 `/token` 接口一致）。

默认基址：`https://api.hifleet.com`。其它部署可设环境变量 **`HIFLEET_API_BASE`**（无末尾斜杠），脚本与 Agent 请求路径均为 `{BASE}/portguide/...`。

---

## 1. 港口列表 / Get ports（检索或全量）

按港口名称、港口代码筛选；**二者均为可选**，可只传其一；**均不传则返回全部港口**（数据量可能很大，建议尽量带条件或分页策略以实际接口为准）。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{BASE}/portguide/getPort/token` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| usertoken | (从配置读取) | 是 | string | 授权 token |
| portName | Shanghai | 否 | string | 港口名称（模糊或精确规则以后端为准） |
| portCode | CNSHA | 否 | string | 港口代码（如 UN/LOCODE 等，以后端为准） |

**portName 与 portCode**：传任意一个即可筛选；也可同时传；**都不传**则返回全部港口列表。

### 与详情接口的衔接

列表响应中每条港口通常含 **`piuid`**（港口内部 id）。调用 **港口详情** 时，将 **`piuid` 的数值作为 Query 参数 `portId`** 传入 `getPortDetail/token`（接口参数名为 `portId`，类型为整数；来源字段名为 `piuid`）。

### 成功响应

以后端实际 JSON 为准。常见形态可能包含 `result` / `status`、`list` 或 `data` 数组；列表项中含 **`piuid`** 供第二步使用。Agent 应原样解析并展示，勿臆造字段。

---

## 2. 港口详情 / Get port detail

根据列表接口返回的 **`piuid`** 查询单港详细信息。

### 请求

| 项目 | 值 |
|------|-----|
| 请求 URL | `{BASE}/portguide/getPortDetail/token` |
| 请求方式 | `GET` |

### Query 参数

| 参数名 | 示例值 | 必选 | 类型 | 说明 |
|--------|--------|------|------|------|
| usertoken | (从配置读取) | 是 | string | 授权 token |
| portId | 12345 | 是 | integer | 港口 id，**取自第一步列表项的 `piuid` 字段** |

---

## 调用流程（Agent）

1. 检查 token；无则提示配置 `HIFLEET_USER_TOKEN` 或 `HIFLEET_USERTOKEN`（或项目中的 `usertoken`）。
2. **列表**：`GET .../portguide/getPort/token?usertoken=...`；若用户给出港名或代码，附加 `portName` 或 `portCode`。
3. **详情**：用户选定某条后，取该条 **`piuid`** → `GET .../portguide/getPortDetail/token?portId={piuid}&usertoken=...`。
4. 若列表命中多条，列出港名/代码/`piuid`，请用户确认后再查详情。

---

## 错误与权限

- 若返回业务错误码或 `status`/`result` 非成功，如实展示接口返回信息。
- 若提示 token 无效或无权限，需检查 HiFleet 账号是否开通港口指南相关接口。
