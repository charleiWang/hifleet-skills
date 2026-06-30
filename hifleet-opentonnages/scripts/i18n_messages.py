#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n for hifleet-opentonnages."""

from __future__ import annotations

import os
from typing import Any

_LOCALE_ENV_KEYS = (
    "HIFLEET_USER_LOCALE",
    "OPENCLAW_USER_LOCALE",
    "OPENCLAW_LOCALE",
    "CURSOR_AGENT_LOCALE",
    "LANG",
)

_MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "skill.reply_language": "Reply in English unless the user uses another language.",
        "config.missing_api_key": "HiFleet API Key is required. See FIRST_SETUP.md.",
        "opentonnages.public_note": "Public listings include full contact details; no unlock step.",
        "opentonnages.no_results_vessel": "No public open vessels matched your criteria.",
        "opentonnages.no_results_cargo": "No public cargo listings matched your criteria.",
        "opentonnages.api_error": "Open market API failed: {detail}",
        "route.redirect_mail": "Private mailbox tonnage → skill **hifleet-mytonnages**.",
        "route.redirect_schedule": "Liner schedules → skill **hifleet-schedule**.",
    },
    "zh": {
        "skill.reply_language": "优先简体中文回复；船名、港口、货物名等保持原文。",
        "config.missing_api_key": "需要配置 HiFleet API Key，请参阅 FIRST_SETUP.md。",
        "opentonnages.public_note": "公开船货盘为全量开放数据，含联系人信息，无需解锁。",
        "opentonnages.no_results_vessel": "未找到符合条件的公开船盘。",
        "opentonnages.no_results_cargo": "未找到符合条件的公开货盘。",
        "opentonnages.api_error": "公开船货盘接口请求失败：{detail}",
        "route.redirect_mail": "个人邮箱船货盘请使用 **hifleet-mytonnages** 技能。",
        "route.redirect_schedule": "班轮船期请使用 **hifleet-schedule** 技能。",
    },
    "zh-CN": {},
    "zh-TW": {
        "skill.reply_language": "優先繁體中文回覆；業務資料保持原文。",
        "config.missing_api_key": "需要設定 HiFleet API Key，請參閱 FIRST_SETUP.md。",
        "opentonnages.public_note": "公開船貨盤為全量開放資料，含聯絡人資訊，無需解鎖。",
        "opentonnages.no_results_vessel": "未找到符合條件的公開船盤。",
        "opentonnages.no_results_cargo": "未找到符合條件的公開貨盤。",
        "opentonnages.api_error": "公開船貨盤介面請求失敗：{detail}",
        "route.redirect_mail": "個人郵箱船貨盤請使用 **hifleet-mytonnages** 技能。",
        "route.redirect_schedule": "班輪船期請使用 **hifleet-schedule** 技能。",
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
