# 安全说明 / Security

本技能为 **HiFleet 船位、档案、PSC、港口指南等查询** 的只读客户端，供 ClawHub 与用户合法查询船舶位置、档案、PSC 检查数据及港口信息。

## 行为说明

- **唯一网络目标**：仅向固定域名发起请求（GET 或 POST，见各接口）。`get_psc_anomalies.py` / `get_psc_openclaw_stats.py` / `get_port.py` 在未设置 `HIFLEET_API_BASE` 时与下列相同；若设置 `HIFLEET_API_BASE`，仅向该基址请求 **同源路径**（`/pscapi/openclaw/...` 或 `/portguide/...`），不扩大路径范围：
  - `https://api.hifleet.com/position/shipSearch`（GET）
  - `https://api.hifleet.com/position/position/get/token`（GET）
  - `https://api.hifleet.com/shiparchive/getShipArchiveWithEnginAndCompany`（GET）
  - `http://api.hifleet.com/position/statisticzonetraffic`（海峡通航统计，**POST**，usertoken 可选，用于扩展时间范围）
  - `https://api.hifleet.com/position/areas/token`（区域清单，GET）
  - `https://api.hifleet.com/position/gettraffic/token`（区域船舶，GET）
  - `https://api.hifleet.com/pscapi/get`（船舶 PSC 检查数据，GET，需 usertoken）
  - `https://api.hifleet.com/pscapi/openclaw/anomalies`（PSC 统计异常列表，GET，需 usertoken）
  - `https://api.hifleet.com/pscapi/openclaw/anomalies/summary`（PSC 统计异常按严重度汇总，GET，需 usertoken）
  - `https://api.hifleet.com/pscapi/openclaw/anomalies/{id}`（PSC 统计异常单条详情，GET，需 usertoken；`{id}` 为数字）
  - `https://api.hifleet.com/pscapi/openclaw/stats/compare`（PSC 宏观区间对比，GET，需 usertoken）
  - `https://api.hifleet.com/pscapi/openclaw/stats/defects/top`（PSC 缺陷码 Top，GET，需 usertoken）
  - `https://api.hifleet.com/pscapi/openclaw/stats/mix/compare`（PSC 旗国/检查类型占比对比，GET，需 usertoken）
  - `https://api.hifleet.com/portguide/getPort/token`（港口列表/检索，GET，需 usertoken）
  - `https://api.hifleet.com/portguide/getPortDetail/token`（港口详情，GET，需 usertoken）
- **无数据外传**：不向上述域名以外的地址发送数据，不上传用户文件或剪贴板。
- **Token 用途**：环境变量 `HIFLEET_USER_TOKEN` / `HIFLEET_USERTOKEN` 仅作为上述 API 的授权参数（海峡通航统计为可选，用于扩展时间范围），由用户自行配置，脚本不写入、不转发至第三方。
- **无动态代码**：脚本仅使用 Python 标准库（`os`, `sys`, `argparse`, `urllib.request`, `urllib.parse`, `json` 等），无 `eval`/`exec`、无 base64 解码执行、无从网络加载代码。

## 脚本清单

| 文件 | 用途 |
|------|------|
| scripts/get_position.py | 按船名/MMSI 查船位，仅 GET 上述 position 接口 |
| scripts/get_archive.py | 按 IMO/MMSI 查档案，仅 GET 上述 shiparchive 接口 |
| scripts/get_strait_traffic.py | 红海/波斯湾海峡通航统计，POST statisticzonetraffic，usertoken 可选（扩展时间范围） |
| scripts/get_areas.py | 区域清单，仅 GET position/areas/token |
| scripts/get_area_traffic.py | 区域船舶，仅 GET position/gettraffic/token，需 usertoken |
| scripts/get_psc.py | 船舶 PSC，GET pscapi/get（及搜船时 GET position/shipSearch），需 usertoken |
| scripts/get_psc_anomalies.py | PSC 统计异常，GET pscapi/openclaw/anomalies*，需 usertoken；可选 `HIFLEET_API_BASE` |
| scripts/get_psc_openclaw_stats.py | PSC 宏观统计，GET pscapi/openclaw/stats/*，需 usertoken；可选 `HIFLEET_API_BASE` |
| scripts/get_port.py | 港口指南，GET portguide/getPort/token、portguide/getPortDetail/token，需 usertoken；可选 `HIFLEET_API_BASE` |

扫描或审核时可对照上述端点与行为；若需进一步说明可联系技能维护方。
