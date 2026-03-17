# 安全说明 / Security

本技能为 **HiFleet 船位与档案查询** 的只读客户端，供 ClawHub 与用户合法查询船舶位置与档案。

## 行为说明

- **唯一网络目标**：仅向固定域名发起 **HTTPS GET** 请求：
  - `https://api.hifleet.com/position/shipSearch`
  - `https://api.hifleet.com/position/position/get/token`
  - `https://api.hifleet.com/shiparchive/getShipArchiveWithEnginAndCompany`
  - `https://api.hifleet.com/traffic/strait`（海峡通航，以 ShowDoc 为准）
  - `https://api.hifleet.com/position/gettraffic/token`（区域船舶）
- **无数据外传**：不向上述域名以外的地址发送数据，不上传用户文件或剪贴板。
- **Token 用途**：环境变量 `HIFLEET_USER_TOKEN` / `HIFLEET_USERTOKEN` 仅作为上述 API 的授权参数（海峡通航为可选，用于扩展时间范围），由用户自行配置，脚本不写入、不转发至第三方。
- **无动态代码**：脚本仅使用 Python 标准库（`os`, `sys`, `urllib.request`, `urllib.parse`, `json`），无 `eval`/`exec`、无 base64 解码执行、无从网络加载代码。

## 脚本清单

| 文件 | 用途 |
|------|------|
| scripts/get_position.py | 按船名/MMSI 查船位，仅 GET 上述 position 接口 |
| scripts/get_archive.py | 按 IMO/MMSI 查档案，仅 GET 上述 shiparchive 接口 |
| scripts/get_strait_traffic.py | 红海/波斯湾海峡通航，仅 GET 海峡通航接口，usertoken 可选 |
| scripts/get_area_traffic.py | 区域船舶，仅 GET position/gettraffic/token，需 usertoken |

扫描或审核时可对照上述端点与行为；若需进一步说明可联系技能维护方。
