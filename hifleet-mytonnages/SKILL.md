---
name: hifleet-mytonnages
version: 1.0.0
description: >
  HiFleet 本地 OpenClaw Skill：路由A=本人邮箱船货盘（memory/SQLite）；路由B=ttseapi 班轮船期（须 hifleet_api_key）。勿伪造数据。执行前须 read_file 分册（见 SKILL 内「必读分册」）。
metadata:
  openclaw:
    homepage: https://mytonnages.hifleet.com
    requires:
      anyBins:
        - python
        - python3
---

## 必读分册（附录正文不得删减）

执行任意工作流前：**`read_file` `SKILL_CONTEXT.md`**（定位、零基础、省 token、SQLite 事实库）、**`read_file` `ROUTING_AND_WHEN.md`**（能力路由 A/B、同轮混合、When to Run）。

**首次启用记忆（memory-lancedb-pro）**：子步骤 A～D 全文 **`MEMORY_LANCEDB.md`**；路由 A 向量检索前须 **`read_file`** 并按该文件执行。

---

## Workflow

### 0. 记忆能力与本 Skill 就绪顺序

1. **（强制）能力路由**：先阅读 **`ROUTING_AND_WHEN.md`**。若当前请求（或其中一部分）属于 **路由 B**，则对该部分仅执行 **Workflow 3**，**不得**用 **Workflow 2** 的邮件同步与解析替代。若属于 **路由 A**，则邮件相关步骤仍按下列第 3～5 步及 **Workflow 2** 全文执行（**2.1～2.7 内部逻辑不变**）。若两类并存，分别执行两套路由。  
2. **若本次请求不含路由 A（仅有路由 B）**：仅执行 **Workflow 3**（含其中 **API Key 检查**），**跳过**下列第 3～5 步。**若含路由 A**：依次执行第 3～5 步；若同轮还含路由 B，路由 B 部分仍完整执行 **Workflow 3**。  
3. **若尚未完成「首次启用记忆：memory-lancedb-pro」且用户将要使用邮件向量检索**：先按 **`MEMORY_LANCEDB.md`** 完成知情同意与安装（或用户明确选择不启用并接受后果）。  
4. **检查邮箱配置**：配置文件路径 `~/.openclaw/workspace/skills/hifleet-mytonnages/config.json`（或当前 OpenClaw 实际路径）。不存在或不完整则进入 **Workflow 1**。  
5. 若记忆与邮箱均已就绪且需要路由 A，进入 **Workflow 2**（邮件查询）。**每次检索类提问均须先完成 2.2 增量同步**；再按 **2.3** 执行「SQLite 结构化查询（如适用）→ 向量检索补充」；对拟送大模型的邮件文本**必须先经 2.3.5 脱敏**再执行 **2.4** 解析；解析完成后按 **2.4.1** 写入 SQLite，再按 **2.4.2** 调用 `ttseapi` 补充船舶档案与 `portid`（须 **`hifleet_api_key`**，见 **`CHARTER_ENRICH_API.md`**），顺序不可省略。用户按**查询港口**查船盘/货盘且需**按距离排序**时，在 **2.3** 命中后按 **2.3.1** 与 **`CHARTER_ENRICH_API.md` §3** 批量算距并升序展示。

### 1. 邮箱配置流程（首次使用或配置缺失时）

**子步骤 1.1～1.4** 全文 **`WORKFLOW_1_MAIL.md`**（与 **Workflow 1** 完全对应，**不得删减、不得改顺序**）。执行前须 **`read_file` `WORKFLOW_1_MAIL.md`**。

### 2. 邮件查询流程（已配置邮箱）

**子步骤 2.1～2.7** 及 **2.3.1、2.3.5、2.4、2.4.1、2.4.2** 全文 **`WORKFLOW_2_MAIL.md`**（与 **Workflow 2** 完全对应，**不得删减、不得重排**）。执行路由 A 时须 **`read_file` `WORKFLOW_2_MAIL.md`**；富化与按距排序须 **`read_file` `CHARTER_ENRICH_API.md`**。

**顺序摘要**：2.1 时间窗 → 2.2 增量同步 → 2.3 SQLite→`memory_search`→合并（含 **2.3.1** 按港距排序）→ 2.3.5 脱敏 → 2.4 按 **`PARSE_SCHEMA.md`** 解析 → 2.4.1 三表写入 → **2.4.2** 船舶档案 + `portid` 富化 → 2.5 筛选 → 2.6 输出与固定链接 → 2.7 `last_used`。

### 3. 船期查询（HiFleet `ttseapi` 班轮接口，路由 B）

**不改变** Workflow 2（2.1～2.7）。接口 URL、Query、Body、`params`、解锁与错误处理等**完整步骤**见 **`SCHEDULE_API.md`**（**不得删减**）。执行路由 B 时须 **`read_file` `SCHEDULE_API.md`**。

## Output 与配置口令

全文 **`WORKFLOW_OUTPUT.md`**（**不得删减含义**）。

## Notes

**日期**：邮件仅月日则补当前年 2026；船龄则建造年 = 2026 − 船龄。**命名**：TBN 保留；多港用 `+`。**安全**：密码 base64 等本地存储；配置权限 600；对话勿显式密码。

**随包文件索引**

```text
~/.openclaw/workspace/skills/hifleet-mytonnages/
├── SKILL.md
├── SKILL_CONTEXT.md         # 定位 + 零基础
├── ROUTING_AND_WHEN.md      # 能力路由 + When to Run
├── MEMORY_LANCEDB.md
├── WORKFLOW_1_MAIL.md
├── WORKFLOW_2_MAIL.md
├── WORKFLOW_OUTPUT.md
├── SCHEDULE_API.md          # 路由 B 班轮船期
├── CHARTER_ENRICH_API.md    # 路由 A：档案 / portid / 按距排序
├── PARSE_SCHEMA.md
├── CONFIG.example.md
├── scripts/charter_facts_tool.py
├── scripts/desensitize_for_llm.py
├── config.json
└── charter_facts.sqlite3 / 向量库（运行时生成）
```

ClawHub 发布说明见 **`PUBLISH.md`**。
