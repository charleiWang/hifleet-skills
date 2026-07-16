# 邮件解析 JSON 规范（路由 A · 2.4）

助手在调用大模型提取船货盘前须读本文件；列名与 `scripts/charter_facts_tool.py` 及 SQLite `cargo_plate` / `openvessel_plate` 一致。

## 规则摘要

- `intent`：字符串数组，元素为 `cargo` / `openvessels` / `unknown` 之一或组合。  
- `data`：含 `cargo`、`openvessels` 数组；无则 `[]`。每条船/货单独对象。  
- 未提及：`null`；日期 `YYYY-MM-DD`；今年缺省年份与 `SKILL.md` Notes 一致。  
- 港口：尽量 UN/LOCODE；多港用 `+`。  
- **船型（openvessels）**：只能填以下六类之一：`散货船`、`集装箱船`、`石油化学品船`、`杂货船`、`油船`、`滚装船`。邮件中的 GC/CONT、MPP、SMAX 等代号或 IHS 细分类型须映射到上述六类；**禁止**将 Geared/Gearless、G'LESS 等吊机描述写入 `船型`。  
- **是否有船吊（openvessels）**：`1`=有吊（Geared）、`0`=无吊（Gearless / G'LESS）；也可在解析阶段保留原文 `geared`/`gearless`，入库时会归一为 `1`/`0`。未提及为 `null`。`吊机数量`>0 时视同有吊。  
- **制裁 / sanctioned（openvessels）**：邮件写明 `sanctioned` / `sanctions` / `制裁` 时，写入 **`O/A其他附加信息`**（原文短语即可）。无船名/IMO 时 enrich 无法调船级制裁接口，但仍会据此打上 **`High Sanction Risk`**。  
- **其它原文 tags**：`geared`/`gearless`、`MPP`、`DG approved`、`box hold`、`CIS`/`BH`/`AUS`、`rightship`/`RS-n`、`eco`、`heavy lift`、`sprinkler` 等，只要邮件/`O/A`/`_email_body` 明确提到，即使无 IMO/船名也会在 enrich/`generate_vessel_tags` 中补上并去重（与接口 tags 合并）。  
- **联系方式**：送大模型前正文须脱敏；**落库前**从原文 `body_text` 抽取 `联系电话`、`即时通讯` 写入 SQLite（见 **`WORKFLOW_2_MAIL.md` §2.3.5**）。  
- **对用户展示（路由 A）**：货盘「装港消约期开始日期」「装港消约期结束日期」、船盘「OPEN开始日期」「OPEN结束日期」在对话中**合并为一行 `Laycan：yyyy/MM/dd~yyyy/MM/dd`**，**不要**分两行写开始/结束；本 JSON **键名不变**，便于 `charter_facts_tool` 入库。

## JSON 结构（须严格遵守键名）

```json
{
  "intent": [],
  "data": {
    "cargo": [
      {
        "客户名称": "",
        "货物数量": null,
        "货物种类": "",
        "装货港": "",
        "卸货港": "",
        "装港消约期开始日期": "",
        "装港消约期结束日期": "",
        "是否为散装": null,
        "装货率": "",
        "装货条款": "",
        "允许船型": "",
        "最早船舶建造年份限制": "",
        "船级限制": "",
        "是否要求船吊": null,
        "是否为危险品": null,
        "冷藏需求": null,
        "舱型要求": "",
        "是否接收甲板货": null,
        "包装要求": "",
        "货物特殊说明": "",
        "货主要求": "",
        "dwt要求": "",
        "联系电话": "",
        "即时通讯": ""
      }
    ],
    "openvessels": [
      {
        "船名": "",
        "IMO": "",
        "船型": "",
        "载重吨": null,
        "建造年份": "",
        "OPEN位置": "",
        "OPEN开始日期": "",
        "OPEN结束日期": "",
        "航线意向": "",
        "吊机数量": null,
        "是否有船吊": null,
        "吊机类型": "",
        "舱口尺寸": "",
        "舱容（立方米）": null,
        "舱数": null,
        "舱盖类型": "",
        "甲板载重能力": "",
        "是否可装危险品": null,
        "冷藏插座数量": null,
        "是否有喷淋系统": null,
        "燃料类型": "",
        "所属公司": "",
        "IMO设备等级": "",
        "船速（节）": null,
        "载货设备描述": "",
        "租船类型": "",
        "是否可跑CIS航线": null,
        "是否可跑BH航线": null,
        "是否可跑AUS航线": null,
        "是否是BOX HOLD": null,
        "是否是NO IRAN/ISRAEL/YEMEN": null,
        "联系电话": "",
        "即时通讯": "",
        "卸货港": "",
        "是否有rightship": null,
        "O/A其他附加信息": ""
      }
    ]
  }
}
```

字段含义与取值约束与历史版 `SKILL.md` 内联注释相同；若与业务邮件冲突，以邮件事实为准。
