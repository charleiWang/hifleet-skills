# config.json 示例（船期路由 B）

将下列字段合并进本 Skill 目录下的 `config.json`（与邮箱等配置同一文件即可）。**勿**把真实 Key 提交到公开仓库。

```json
{
  "hifleet_api_key": "在 HiFleet 网站获取的 API Key（与账号绑定、按次计费）",
  "hifleet_liner_api_base": "https://ttseapi.hifleet.com/openclaw/vessel/charter/liner",
  "hifleet_charter_api_base": "https://ttseapi.hifleet.com/openclaw/vessel/charter"
}
```

- `hifleet_api_key`：路由 A 富化（船舶档案、港口 ID、港距）与路由 B 班轮船期**共用**；必填（或等价环境变量 `HIFLEET_API_KEY`，见 `SKILL.md`）。技能安装目录名为 **`hifleet-mytonnages`** 时，`config.json` 位于该目录下。
- `hifleet_liner_api_base`：可选，路由 B 默认如上；私有化/联调时可改。
- `hifleet_charter_api_base`：可选，路由 A 富化与按距排序默认如上；见 **`CHARTER_ENRICH_API.md`**。
