# User wording (mandatory)

## Say → Do not say

| Avoid (internal) | Use with user |
|------------------|---------------|
| unlock, decrypt, typeCode | *(not used — data is fully public)* |
| route V / G | **公开船盘** / **公开货盘** / **HiFleet 平台船货** |
| vessels/search, cargo/search | **在 HiFleet 公开市场上查询** |
| enrich-row | **补充船舶档案 / 标签 / 港距**（增值服务） |
| mytonnages SQLite | **您邮箱里的船货** → other skill |

## Product message (v1.0)

- Public listings **include contacts** — no “pay to unlock phone number”.
- Optional **enrich** adds archive, tags, distance (API points).

## Redirects

| User wants | Skill |
|------------|--------|
| My **email** | **hifleet-mytonnages** |
| **Liner** schedule | **hifleet-schedule** |
| **Pre-arrival** | **hifleet-mytonnages** |
| **Public** open tonnage/cargo | **hifleet-opentonnages** (this) |
