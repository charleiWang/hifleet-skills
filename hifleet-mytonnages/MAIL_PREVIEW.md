# 原始邮件预览（路由 A）

用户在前端点击 **「查看原邮件」** 时，跳转到本 Skill 提供的 **本地预览页**（非 Gmail/163 网页）。

## 架构

```text
定时同步 mail_parse_loop
  → IMAP FETCH RFC822
  → mail_archive/{token}.eml + mail_index 表

前端按钮 preview_url
  → mail_preview_server HTTP
  → 优先读本地 .eml，缺失则 IMAP 按 Message-ID/UID 拉取
  → HTML 预览（正文 + 附件下载）
```

## 1. 启动预览服务

与智能体同机部署（需能读 `config.json` 与 `mail_archive/`）：

```bash
cd hifleet-skills/hifleet-mytonnages
python scripts/mail_preview_server.py
# 或指定监听
python scripts/mail_preview_server.py --host 0.0.0.0 --port 8765
```

健康检查：`GET http://localhost:8765/health`

## 2. config.json

```json
{
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "email": "user@example.com",
  "email_password": "app-password",
  "imap_mailbox": "INBOX",
  "mail_preview_host": "0.0.0.0",
  "mail_preview_port": 8765,
  "mail_preview_base_url": "http://your-server:8765",
  "mail_preview_token": "optional-shared-secret"
}
```

| 配置 | 说明 |
|------|------|
| `mail_preview_base_url` | 写入 `preview_url` 的公网/内网根地址（**前端按钮用此**） |
| `mail_preview_token` | 可选；设置后请求须带 `?auth=` 或头 `X-HIFLEET-Preview-Token` |

环境变量：`HIFLEET_MAIL_PREVIEW_HOST` / `PORT` / `BASE_URL` / `TOKEN`

## 3. 前端集成

### 方式 A：检索结果已带链接（推荐）

`search` / `query-by-port` JSON 每行含 **`preview_url`**：

```bash
python scripts/charter_facts_tool.py search "bulk carrier"
```

```json
{
  "message_id": "<abc@mail.example>",
  "subject": "OPEN TONNAGE",
  "preview_url": "http://your-server:8765/mail/preview/a1b2c3..."
}
```

按钮示例：

```html
<a href="{{ preview_url }}" target="_blank" rel="noopener noreferrer">
  查看原邮件
</a>
```

### 方式 B：按 Message-ID 换 URL

```http
GET /api/mail/preview-url?message_id=%3Cabc%40mail.example%3E
```

响应：

```json
{
  "ok": true,
  "message_id": "<abc@mail.example>",
  "preview_token": "a1b2c3...",
  "preview_url": "http://your-server:8765/mail/preview/a1b2c3..."
}
```

CLI：

```bash
python scripts/charter_facts_tool.py preview-url --message-id "<abc@mail.example>"
```

## 4. HTTP 路由

| 路径 | 说明 |
|------|------|
| `GET /mail/preview/{token}` | **预览页**（前端按钮跳转目标） |
| `GET /mail/attachment/{token}/{index}` | 附件下载 |
| `GET /api/mail/preview-url?message_id=` | 生成 preview_url |
| `GET /api/mail/raw/{token}` | JSON 元数据+正文（供自定义 UI） |
| `GET /health` | 存活探测 |

`{token}` = `sha256(message_id)[:32]`（与 `preview_url` 路径一致）

## 5. 数据存储

| 位置 | 内容 |
|------|------|
| `mail_archive/*.eml` | 完整 RFC822 |
| SQLite `mail_index` | message_id、preview_token、imap_uid、archive_path |
| `cargo_plate` / `openvessel_plate` | 仅解析字段（**不含**正文） |

历史邮件若尚无 `.eml`，首次打开预览时会 **IMAP 按需拉取** 并写入归档。

## 6. Agent 规则

- 展示船盘/货盘列表时，若有 `preview_url`，向用户提供 **「查看原邮件」** 可点击链接。
- 对用户话术见 **`USER_WORDING.md`**（不说 IMAP/RFC822）。
- 预览服务须已启动；否则提示管理员运行 `mail_preview_server.py`。

## 7. 限制

- 邮件已删或移出 `imap_mailbox` 且本地无 `.eml` → 404。
- 无 `Message-ID` 的邮件（`generated-@local`）可能无法 IMAP 搜索。
- HTML 正文经简单消毒；复杂邮件版式可能略有差异。
