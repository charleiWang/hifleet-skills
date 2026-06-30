#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""User-facing messages: English source keys; translate per agent locale. Do NOT translate business data."""

from __future__ import annotations

import os
import re
from typing import Any

# Locale resolution (first match wins)
_LOCALE_ENV_KEYS = (
    "HIFLEET_USER_LOCALE",
    "OPENCLAW_USER_LOCALE",
    "OPENCLAW_LOCALE",
    "CURSOR_AGENT_LOCALE",
    "LANG",
)

_MESSAGES: dict[str, dict[str, str]] = {
  "en": {
    "skill.reply_language": "Reply to the user in English unless they write in another language.",
    "llm.json_parse_failed": (
      "Email parsing failed: the model response was not valid JSON. "
      "This often happens when the email or attachments are too long and exceed the model input/output token limit."
    ),
    "llm.token_limit_hint": (
      "Ask your administrator to raise LLM limits, for example:\n"
      "• Output: environment variable CHARTER_LLM_MAX_OUTPUT_TOKENS (default 65536)\n"
      "• Input: shorten very long emails/attachments, or split parsing across batches\n"
      "• Agent settings: increase max output tokens / context window in the LLM provider panel"
    ),
    "llm.parse_retry": "The message will be retried on the next scheduled parse (every 10 minutes).",
    "config.missing_api_key": "HiFleet API Key is required. See FIRST_SETUP.md to configure hifleet_api_key.",
    "config.missing_email": "Email (IMAP) configuration is required for mailbox tonnage/cargo queries.",
    "schedule.redirect": "Liner schedules (bulk / Ro-Ro / container) moved to skill **hifleet-schedule**.",
    "opentonnages.redirect": "Public open tonnage/cargo moved to skill **hifleet-opentonnages** (fully open, no unlock).",
  },
  "zh": {
    "skill.reply_language": "除用户主动使用其他语言外，优先用简体中文回复；业务数据（船名、港口、货物名等）保持原文。",
    "llm.json_parse_failed": (
      "邮件解析失败：模型返回内容不是有效 JSON。"
      "常见原因是邮件或附件过长，超出大模型输入/输出 token 上限。"
    ),
    "llm.token_limit_hint": (
      "请管理员或您在智能体/模型设置中调高 token 限制，例如：\n"
      "• 输出上限：环境变量 CHARTER_LLM_MAX_OUTPUT_TOKENS（默认 65536）\n"
      "• 输入侧：过长邮件/附件可缩短或分批解析\n"
      "• 智能体前端：在所用大模型配置里提高「最大输出 token」和「上下文长度」"
    ),
    "llm.parse_retry": "该邮件将在下一轮定时解析（每 10 分钟）时重试。",
    "config.missing_api_key": "需要配置 HiFleet API Key，请在 FIRST_SETUP.md 中设置 hifleet_api_key。",
    "config.missing_email": "查询邮箱船货盘需要先配置邮箱（IMAP）。",
    "schedule.redirect": "班轮船期（散杂货/滚装/集装箱）已独立为 **hifleet-schedule** 技能。",
    "opentonnages.redirect": "公开船盘/公开货盘已独立为 **hifleet-opentonnages** 技能（全公开，无需解锁）。",
  },
  "zh-CN": {},  # alias filled below
  "zh-TW": {
    "skill.reply_language": "除使用者主動使用其他語言外，優先以繁體中文回覆；業務資料（船名、港口、貨物名等）保持原文。",
    "llm.json_parse_failed": (
      "郵件解析失敗：模型回傳內容不是有效 JSON。"
      "常見原因是郵件或附件過長，超出大模型輸入/輸出 token 上限。"
    ),
    "llm.token_limit_hint": (
      "請管理員或在智慧體/模型設定中調高 token 限制，例如：\n"
      "• 輸出上限：環境變數 CHARTER_LLM_MAX_OUTPUT_TOKENS（預設 65536）\n"
      "• 輸入側：過長郵件/附件可縮短或分批解析\n"
      "• 智慧體前端：在所用大模型設定裡提高「最大輸出 token」與「上下文長度」"
    ),
    "llm.parse_retry": "該郵件將在下一輪定時解析（每 10 分鐘）時重試。",
    "config.missing_api_key": "需要設定 HiFleet API Key，請參閱 FIRST_SETUP.md 設定 hifleet_api_key。",
    "config.missing_email": "查詢郵箱船貨盤需要先設定郵箱（IMAP）。",
    "schedule.redirect": "班輪船期（散雜貨/滾裝/集裝箱）已獨立為 **hifleet-schedule** 技能。",
    "opentonnages.redirect": "公開船盤/公開貨盤已獨立為 **hifleet-opentonnages** 技能（全公開，無需解鎖）。",
  },
}

_MESSAGES["zh-CN"] = _MESSAGES["zh"]


def resolve_user_locale() -> str:
    for key in _LOCALE_ENV_KEYS:
        raw = os.environ.get(key, "").strip()
        if not raw:
            continue
        loc = raw.split(".")[0].replace("_", "-")
        if loc.lower().startswith("zh"):
            if "tw" in loc.lower() or "hant" in raw.lower():
                return "zh-TW"
            return "zh"
        if loc.lower().startswith("en"):
            return "en"
        return loc
    return "en"


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    loc = locale or resolve_user_locale()
    table = _MESSAGES.get(loc) or _MESSAGES.get(loc.split("-")[0]) or _MESSAGES["en"]
    msg = table.get(key) or _MESSAGES["en"].get(key) or key
    if kwargs:
        try:
            return msg.format(**kwargs)
        except (KeyError, ValueError):
            return msg
    return msg


def is_llm_json_parse_error(exc: BaseException) -> bool:
    s = str(exc).lower()
    return (
        "did not contain a json" in s
        or "json object" in s
        or "jsondecodeerror" in s
        or "未匹配到 json" in s
        or "not valid json" in s
    )


def is_llm_token_limit_error(exc: BaseException) -> bool:
    s = str(exc).lower()
    return (
        "finish_reason=length" in s
        or "max_tokens" in s
        or "token limit" in s
        or "context length" in s
        or "maximum context" in s
        or "too long" in s
        or re.search(r"\b128k\b|\b32k\b", s) is not None
    )


def format_llm_parse_error_for_user(exc: BaseException, locale: str | None = None) -> str:
    lines = [t("llm.json_parse_failed", locale)]
    if is_llm_token_limit_error(exc) or is_llm_json_parse_error(exc):
        lines.append("")
        lines.append(t("llm.token_limit_hint", locale))
    lines.append("")
    lines.append(t("llm.parse_retry", locale))
    return "\n".join(lines)
