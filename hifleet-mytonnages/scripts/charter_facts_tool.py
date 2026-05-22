#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hifleet-mytonnages：解析结果写入 / 检索 charter_facts.sqlite3（货盘表 + 船盘表 + unknown 表）。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# 与 SKILL.md §2.4 JSON 键一致
CARGO_FIELD_KEYS: tuple[str, ...] = (
    "客户名称",
    "货物数量",
    "货物种类",
    "装货港",
    "卸货港",
    "装港消约期开始日期",
    "装港消约期结束日期",
    "是否为散装",
    "装货率",
    "装货条款",
    "允许船型",
    "最早船舶建造年份限制",
    "船级限制",
    "是否要求船吊",
    "是否为危险品",
    "冷藏需求",
    "舱型要求",
    "是否接收甲板货",
    "包装要求",
    "货物特殊说明",
    "货主要求",
    "dwt要求",
    "联系电话",
    "即时通讯",
)

OPENVESSEL_FIELD_KEYS: tuple[str, ...] = (
    "船名",
    "IMO",
    "船型",
    "载重吨",
    "建造年份",
    "OPEN位置",
    "OPEN开始日期",
    "OPEN结束日期",
    "航线意向",
    "吊机数量",
    "是否有船吊",
    "吊机类型",
    "舱口尺寸",
    "舱容（立方米）",
    "舱数",
    "舱盖类型",
    "甲板载重能力",
    "是否可装危险品",
    "冷藏插座数量",
    "是否有喷淋系统",
    "燃料类型",
    "所属公司",
    "IMO设备等级",
    "船速（节）",
    "载货设备描述",
    "租船类型",
    "是否可跑CIS航线",
    "是否可跑BH航线",
    "是否可跑AUS航线",
    "是否是BOX HOLD",
    "是否是NO IRAN/ISRAEL/YEMEN",
    "联系电话",
    "即时通讯",
    "卸货港",
    "是否有rightship",
    "O/A其他附加信息",
)

CARGO_INT_KEYS = {
    "货物数量",
    "是否为散装",
    "是否要求船吊",
    "是否为危险品",
    "冷藏需求",
    "是否接收甲板货",
}

OPENVESSEL_INT_KEYS = {
    "载重吨",
    "吊机数量",
    "是否有船吊",
    "舱容（立方米）",
    "舱数",
    "是否可装危险品",
    "冷藏插座数量",
    "是否有喷淋系统",
    "是否可跑CIS航线",
    "是否可跑BH航线",
    "是否可跑AUS航线",
    "是否是BOX HOLD",
    "是否是NO IRAN/ISRAEL/YEMEN",
    "是否有rightship",
}

OPENVESSEL_REAL_KEYS = {"船速（节）"}

# 2.4.2 富化列（与 CHARTER_ENRICH_API.md 一致）
CARGO_ENRICH_KEYS: tuple[str, ...] = ("portid", "discharging_portid")

SHIP_ARCHIVE_KEYS: tuple[str, ...] = (
    "档案_船名",
    "档案_呼号",
    "档案_建造年",
    "档案_dwt",
    "档案_船旗",
    "档案_船长",
    "档案_船宽",
    "档案_吃水",
    "档案_总吨",
    "档案_造船厂",
    "档案_船型",
    "档案_船东",
    "档案_经营人",
    "档案_管理公司",
    "档案_细分船型",
    "ship_archive_json",
)

OPENVESSEL_ENRICH_KEYS: tuple[str, ...] = ("portid", "discharging_portid") + SHIP_ARCHIVE_KEYS

DEFAULT_CHARTER_API_BASE = "https://ttseapi.hifleet.com/openclaw/vessel/charter"


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _norm_intent(intent: Any) -> list[str]:
    if intent is None:
        return []
    if isinstance(intent, str):
        return [intent] if intent else []
    if isinstance(intent, list):
        return [str(x) for x in intent if x is not None]
    return [str(intent)]


def coerce_field(key: str, val: Any, int_keys: set[str], real_keys: set[str]) -> Any:
    if val is None:
        return None
    if key in int_keys:
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return int(val)
        s = str(val).strip()
        if not s or s.lower() in ("null", "none"):
            return None
        m = re.search(r"-?\d+", s)
        return int(m.group(0)) if m else None
    if key in real_keys:
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
        s = str(val).strip()
        if not s or s.lower() in ("null", "none"):
            return None
        try:
            return float(s.replace(",", ""))
        except ValueError:
            m = re.search(r"-?\d+\.?\d*", s)
            return float(m.group(0)) if m else None
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return val if isinstance(val, str) else str(val)


def _search_parts(
    subject: str,
    from_addr: str,
    row: dict[str, Any],
    keys: Iterable[str],
) -> str:
    parts = [subject or "", from_addr or ""]
    for k in keys:
        v = row.get(k)
        if v is not None and v != "":
            parts.append(str(v))
    return " ".join(parts)


class CharterFactsDB:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def init(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}

        if "charter_fact" in tables:
            cur.execute("DROP TABLE IF EXISTS charter_fact")

        if "cargo_plate" in tables:
            cur.execute("PRAGMA table_info(cargo_plate)")
            cols = {r[1] for r in cur.fetchall()}
            if "客户名称" not in cols:
                cur.execute("DROP TABLE IF EXISTS cargo_plate")
                cur.execute("DROP TABLE IF EXISTS openvessel_plate")
                cur.execute("DROP TABLE IF EXISTS mail_unknown")

        cargo_cols = ", ".join(f'{_q(k)} TEXT' for k in CARGO_FIELD_KEYS)
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS cargo_plate (
              message_id TEXT NOT NULL,
              email_date_utc TEXT,
              from_addr TEXT,
              subject TEXT,
              row_index INTEGER NOT NULL,
              {cargo_cols},
              payload_json TEXT NOT NULL,
              search_text TEXT NOT NULL,
              parsed_at TEXT NOT NULL
            )
            """
        )

        opv_cols = ", ".join(f'{_q(k)} TEXT' for k in OPENVESSEL_FIELD_KEYS)
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS openvessel_plate (
              message_id TEXT NOT NULL,
              email_date_utc TEXT,
              from_addr TEXT,
              subject TEXT,
              row_index INTEGER NOT NULL,
              {opv_cols},
              payload_json TEXT NOT NULL,
              search_text TEXT NOT NULL,
              parsed_at TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mail_unknown (
              message_id TEXT NOT NULL,
              email_date_utc TEXT,
              from_addr TEXT,
              subject TEXT,
              intent_json TEXT NOT NULL,
              search_text TEXT NOT NULL,
              parsed_at TEXT NOT NULL
            )
            """
        )

        self._ensure_columns(conn, "cargo_plate", CARGO_ENRICH_KEYS)
        self._ensure_columns(conn, "openvessel_plate", OPENVESSEL_ENRICH_KEYS)
        conn.commit()

    def _ensure_columns(self, conn: sqlite3.Connection, table: str, keys: tuple[str, ...]) -> None:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        existing = {r[1] for r in cur.fetchall()}
        for k in keys:
            if k not in existing:
                cur.execute(f'ALTER TABLE {table} ADD COLUMN {_q(k)} TEXT')


def _row_index_key(message_id: str, row_index: Any, fact_type: str) -> str:
    return f"{message_id}:{row_index}:{fact_type}"

    def save_parsed(
        self,
        conn: sqlite3.Connection,
        *,
        message_id: str,
        email_date_utc: str,
        from_addr: str,
        subject: str,
        parsed: dict[str, Any],
    ) -> None:
        self.init(conn)
        cur = conn.cursor()
        intent = _norm_intent(parsed.get("intent"))
        data = parsed.get("data") or {}
        cargo_list = data.get("cargo") if isinstance(data.get("cargo"), list) else []
        opv_list = data.get("openvessels") if isinstance(data.get("openvessels"), list) else []

        cur.execute("DELETE FROM cargo_plate WHERE message_id = ?", (message_id,))
        cur.execute("DELETE FROM openvessel_plate WHERE message_id = ?", (message_id,))
        cur.execute("DELETE FROM mail_unknown WHERE message_id = ?", (message_id,))

        parsed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cargo_cols_list = [_q(k) for k in CARGO_FIELD_KEYS]
        cargo_placeholders = ", ".join(["?"] * (5 + len(CARGO_FIELD_KEYS) + 3))
        cargo_insert = (
            f'INSERT INTO cargo_plate (message_id, email_date_utc, from_addr, subject, row_index, '
            f'{", ".join(cargo_cols_list)}, payload_json, search_text, parsed_at) VALUES ({cargo_placeholders})'
        )

        for idx, raw in enumerate(cargo_list):
            if not isinstance(raw, dict):
                continue
            row_vals: dict[str, Any] = {}
            for k in CARGO_FIELD_KEYS:
                row_vals[k] = coerce_field(k, raw.get(k), CARGO_INT_KEYS, set())
            payload = json.dumps(raw, ensure_ascii=False)
            st = _search_parts(subject, from_addr, row_vals, CARGO_FIELD_KEYS)
            vals: list[Any] = [
                message_id,
                email_date_utc,
                from_addr,
                subject,
                idx,
            ]
            vals.extend(row_vals[k] for k in CARGO_FIELD_KEYS)
            vals.extend([payload, st, parsed_at])
            cur.execute(cargo_insert, vals)

        opv_cols_list = [_q(k) for k in OPENVESSEL_FIELD_KEYS]
        opv_placeholders = ", ".join(["?"] * (5 + len(OPENVESSEL_FIELD_KEYS) + 3))
        opv_insert = (
            f'INSERT INTO openvessel_plate (message_id, email_date_utc, from_addr, subject, row_index, '
            f'{", ".join(opv_cols_list)}, payload_json, search_text, parsed_at) VALUES ({opv_placeholders})'
        )

        for idx, raw in enumerate(opv_list):
            if not isinstance(raw, dict):
                continue
            row_vals = {}
            for k in OPENVESSEL_FIELD_KEYS:
                row_vals[k] = coerce_field(k, raw.get(k), OPENVESSEL_INT_KEYS, OPENVESSEL_REAL_KEYS)
            payload = json.dumps(raw, ensure_ascii=False)
            st = _search_parts(subject, from_addr, row_vals, OPENVESSEL_FIELD_KEYS)
            vals = [message_id, email_date_utc, from_addr, subject, idx]
            vals.extend(row_vals[k] for k in OPENVESSEL_FIELD_KEYS)
            vals.extend([payload, st, parsed_at])
            cur.execute(opv_insert, vals)

        has_unknown = any(x.lower() == "unknown" for x in intent)
        if has_unknown and not cargo_list and not opv_list:
            st = " ".join(
                x for x in (subject, from_addr, json.dumps(intent, ensure_ascii=False)) if x
            )
            cur.execute(
                "INSERT INTO mail_unknown (message_id, email_date_utc, from_addr, subject, intent_json, search_text, parsed_at) VALUES (?,?,?,?,?,?,?)",
                (
                    message_id,
                    email_date_utc,
                    from_addr,
                    subject,
                    json.dumps(intent, ensure_ascii=False),
                    st,
                    parsed_at,
                ),
            )

        conn.commit()

    def search(self, conn: sqlite3.Connection, q: str, limit: int = 50) -> list[dict[str, Any]]:
        self.init(conn)
        cur = conn.cursor()
        like = f"%{q}%"
        out: list[dict[str, Any]] = []

        for table, ftype in (
            ("cargo_plate", "cargo"),
            ("openvessel_plate", "openvessel"),
        ):
            cur.execute(
                f"SELECT * FROM {table} WHERE search_text LIKE ? ORDER BY email_date_utc DESC LIMIT ?",
                (like, limit),
            )
            for row in cur.fetchall():
                d = dict(row)
                d["_source_table"] = table
                d["_fact_type"] = ftype
                pj = d.get("payload_json")
                if pj:
                    try:
                        d["payload"] = json.loads(pj)
                    except json.JSONDecodeError:
                        d["payload"] = None
                out.append(d)

        cur.execute(
            "SELECT * FROM mail_unknown WHERE search_text LIKE ? ORDER BY email_date_utc DESC LIMIT ?",
            (like, limit),
        )
        for row in cur.fetchall():
            d = dict(row)
            d["_source_table"] = "mail_unknown"
            d["_fact_type"] = "unknown"
            ij = d.get("intent_json")
            if ij:
                try:
                    d["intent"] = json.loads(ij)
                except json.JSONDecodeError:
                    d["intent"] = None
            out.append(d)

        return out[:limit]


def default_db_path() -> Path:
    return Path.home() / ".openclaw" / "workspace" / "skills" / "hifleet-mytonnages" / "charter_facts.sqlite3"


def default_skill_dir() -> Path:
    return Path.home() / ".openclaw" / "workspace" / "skills" / "hifleet-mytonnages"


def load_api_config() -> tuple[str, str]:
    api_key = os.environ.get("HIFLEET_API_KEY", "").strip()
    api_base = os.environ.get("HIFLEET_CHARTER_API_BASE", DEFAULT_CHARTER_API_BASE).strip()
    cfg_path = default_skill_dir() / "config.json"
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            api_key = api_key or str(cfg.get("hifleet_api_key") or "").strip()
            api_base = (
                os.environ.get("HIFLEET_CHARTER_API_BASE")
                or str(cfg.get("hifleet_charter_api_base") or api_base).strip()
            )
        except (json.JSONDecodeError, OSError):
            pass
    return api_key, api_base.rstrip("/")


def _http_post_json(url: str, body: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _api_ok(payload: dict[str, Any]) -> bool:
    st = payload.get("status")
    return st == "1" or st == 1


def _map_archive_item(item: dict[str, Any]) -> dict[str, str | None]:
    return {
        "档案_船名": str(item.get("ShipName") or "") or None,
        "档案_呼号": str(item.get("callsign") or "") or None,
        "档案_建造年": str(item.get("YearOfBuild") or "") or None,
        "档案_dwt": str(item.get("dwt") if item.get("dwt") is not None else "") or None,
        "档案_船旗": str(item.get("flagname") or "") or None,
        "档案_船长": str(item.get("Length") if item.get("Length") is not None else "") or None,
        "档案_船宽": str(item.get("width") if item.get("width") is not None else "") or None,
        "档案_吃水": str(item.get("draught") if item.get("draught") is not None else "") or None,
        "档案_总吨": str(item.get("GrossTonnage") if item.get("GrossTonnage") is not None else "") or None,
        "档案_造船厂": str(item.get("Shipbuilder") or "") or None,
        "档案_船型": str(item.get("type") or "") or None,
        "档案_船东": str(item.get("registeredOwner") or "") or None,
        "档案_经营人": str(item.get("operator") or "") or None,
        "档案_管理公司": str(item.get("shipManager") or "") or None,
        "档案_细分船型": str(item.get("minotype") or "") or None,
        "ship_archive_json": json.dumps(item, ensure_ascii=False),
    }


def _normalize_portname(name: str | None) -> str | None:
    if not name:
        return None
    s = str(name).strip()
    if not s or s.lower() in ("null", "none", "未提及"):
        return None
    return s.replace("/", "+").replace(",", "+")


def _fetch_portid_batch(api_base: str, api_key: str, portnames: list[str]) -> dict[str, str]:
    """portname -> portid 串。"""
    unique = []
    seen: set[str] = set()
    for p in portnames:
        if p and p not in seen:
            seen.add(p)
            unique.append(p)
    if not unique:
        return {}
    joined = "+".join(unique)
    url = f"{api_base}/port/portid?{urllib.parse.urlencode({'api_key': api_key})}"
    try:
        resp = _http_post_json(url, {"portname": joined})
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}
    if not _api_ok(resp):
        return {}
    data = resp.get("data") or {}
    pid = data.get("portid")
    if not pid:
        return {}
    if len(unique) == 1:
        return {unique[0]: str(pid)}
    parts = [x.strip() for x in str(pid).split(",")]
    out: dict[str, str] = {}
    for i, name in enumerate(unique):
        if i < len(parts):
            out[name] = parts[i]
        else:
            out[name] = str(pid)
    return out


def _fetch_ship_archives(api_base: str, api_key: str, imos: list[str]) -> dict[str, dict[str, str | None]]:
    if not imos:
        return {}
    url = f"{api_base}/ship-archive/batch?{urllib.parse.urlencode({'api_key': api_key})}"
    try:
        resp = _http_post_json(url, {"imos": imos})
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}
    if not _api_ok(resp):
        return {}
    data = resp.get("data") or {}
    lst = data.get("list") if isinstance(data.get("list"), list) else []
    out: dict[str, dict[str, str | None]] = {}
    for item in lst:
        if not isinstance(item, dict):
            continue
        imo = str(item.get("imo") or "").strip()
        if imo:
            out[imo] = _map_archive_item(item)
    return out


def _fetch_distances(
    api_base: str,
    api_key: str,
    query_portid: str,
    index_data: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    if not query_portid or not index_data:
        return {}
    url = f"{api_base}/port-distances/batch?{urllib.parse.urlencode({'api_key': api_key})}"
    try:
        resp = _http_post_json(
            url,
            {"queryPortid": query_portid, "indexData": index_data},
        )
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}
    if not _api_ok(resp):
        return {}
    data = resp.get("data") or {}
    lst = data.get("list") if isinstance(data.get("list"), list) else []
    out: dict[str, dict[str, Any]] = {}
    for item in lst:
        if not isinstance(item, dict):
            continue
        idx = str(item.get("index") or "")
        if idx:
            out[idx] = item
    return out


def enrich_database(db_path: Path) -> dict[str, Any]:
    api_key, api_base = load_api_config()
    if not api_key:
        return {"ok": False, "error": "missing hifleet_api_key"}

    db = CharterFactsDB(db_path)
    conn = db.connect()
    stats = {"openvessel_updated": 0, "cargo_updated": 0, "imos_fetched": 0, "ports_fetched": 0}
    try:
        db.init(conn)
        cur = conn.cursor()

        cur.execute(
            'SELECT message_id, row_index, "IMO", "OPEN位置", "卸货港" FROM openvessel_plate'
        )
        opv_rows = [dict(r) for r in cur.fetchall()]
        imos = []
        for r in opv_rows:
            imo = str(r.get("IMO") or "").strip()
            imo_digits = re.sub(r"\D", "", imo)
            if imo_digits:
                imos.append(imo_digits)
        imos_unique = list(dict.fromkeys(imos))
        archives = _fetch_ship_archives(api_base, api_key, imos_unique)
        stats["imos_fetched"] = len(archives)

        port_names: list[str] = []
        for r in opv_rows:
            for col in ("OPEN位置", "卸货港"):
                pn = _normalize_portname(r.get(col))
                if pn:
                    port_names.append(pn)
        cur.execute(
            'SELECT message_id, row_index, "装货港", "卸货港" FROM cargo_plate'
        )
        cargo_rows = [dict(r) for r in cur.fetchall()]
        for r in cargo_rows:
            for col in ("装货港", "卸货港"):
                pn = _normalize_portname(r.get(col))
                if pn:
                    port_names.append(pn)
        port_map = _fetch_portid_batch(api_base, api_key, port_names)
        stats["ports_fetched"] = len(port_map)

        for r in opv_rows:
            mid, ridx = r["message_id"], r["row_index"]
            updates: dict[str, Any] = {}
            open_pn = _normalize_portname(r.get("OPEN位置"))
            if open_pn and open_pn in port_map:
                updates["portid"] = port_map[open_pn]
            dis_pn = _normalize_portname(r.get("卸货港"))
            if dis_pn and dis_pn in port_map:
                updates["discharging_portid"] = port_map[dis_pn]
            imo_digits = re.sub(r"\D", "", str(r.get("IMO") or ""))
            if imo_digits and imo_digits in archives:
                arch = archives[imo_digits]
                updates.update(arch)
                if arch.get("档案_dwt"):
                    updates["载重吨"] = arch["档案_dwt"]
                if arch.get("档案_建造年"):
                    updates["建造年份"] = arch["档案_建造年"]
                if arch.get("档案_船型"):
                    updates["船型"] = arch["档案_船型"]
                if arch.get("档案_船名"):
                    updates["船名"] = arch["档案_船名"]
            if updates:
                sets = ", ".join(f"{_q(k)} = ?" for k in updates)
                vals = list(updates.values()) + [mid, ridx]
                cur.execute(
                    f"UPDATE openvessel_plate SET {sets} WHERE message_id = ? AND row_index = ?",
                    vals,
                )
                stats["openvessel_updated"] += 1

        for r in cargo_rows:
            mid, ridx = r["message_id"], r["row_index"]
            updates = {}
            load_pn = _normalize_portname(r.get("装货港"))
            if load_pn and load_pn in port_map:
                updates["portid"] = port_map[load_pn]
            dis_pn = _normalize_portname(r.get("卸货港"))
            if dis_pn and dis_pn in port_map:
                updates["discharging_portid"] = port_map[dis_pn]
            if updates:
                sets = ", ".join(f"{_q(k)} = ?" for k in updates)
                vals = list(updates.values()) + [mid, ridx]
                cur.execute(
                    f"UPDATE cargo_plate SET {sets} WHERE message_id = ? AND row_index = ?",
                    vals,
                )
                stats["cargo_updated"] += 1

        conn.commit()
    finally:
        conn.close()
    return {"ok": True, **stats}


def query_by_port(db_path: Path, port: str, limit: int = 50) -> list[dict[str, Any]]:
    api_key, api_base = load_api_config()
    if not api_key:
        return [{"_error": "missing hifleet_api_key"}]

    db = CharterFactsDB(db_path)
    conn = db.connect()
    results: list[dict[str, Any]] = []
    try:
        db.init(conn)
        cur = conn.cursor()
        q_pn = _normalize_portname(port)
        if not q_pn:
            return [{"_error": "empty port name"}]

        port_map = _fetch_portid_batch(api_base, api_key, [q_pn])
        query_portid = port_map.get(q_pn) or ""
        if not query_portid:
            query_portid = str(port_map.values())[0] if port_map else ""
        if not query_portid:
            return [{"_error": f"portid not resolved for {port}"}]
        query_portid = query_portid.split(",")[0].strip()

        candidates: list[dict[str, Any]] = []
        for table, ftype in (("openvessel_plate", "openvessel"), ("cargo_plate", "cargo")):
            cur.execute(f"SELECT * FROM {table} WHERE portid IS NOT NULL AND portid != ''")
            for row in cur.fetchall():
                d = dict(row)
                d["_fact_type"] = ftype
                d["_source_table"] = table
                candidates.append(d)

        index_data = []
        for d in candidates:
            ftype = d.get("_fact_type", "")
            idx_key = _row_index_key(
                str(d.get("message_id") or ""),
                d.get("row_index"),
                str(ftype),
            )
            pid = d.get("portid")
            if not pid:
                continue
            d["_index_key"] = idx_key
            index_data.append({"index": idx_key, "portid": str(pid)})

        dist_map = _fetch_distances(api_base, api_key, query_portid, index_data)

        for d in candidates:
            idx_key = d.get("_index_key", "")
            dist_info = dist_map.get(idx_key) or {}
            d["query_port"] = port
            d["query_portid"] = query_portid
            d["dist"] = dist_info.get("dist")
            d["nearestPortId"] = dist_info.get("nearestPortId")
            pj = d.get("payload_json")
            if pj:
                try:
                    d["payload"] = json.loads(pj)
                except json.JSONDecodeError:
                    d["payload"] = None
            results.append(d)

        results.sort(
            key=lambda x: (
                x.get("dist") is None,
                float(x.get("dist") if x.get("dist") is not None else 1e18),
            )
        )
        return results[:limit]
    finally:
        conn.close()


def cmd_save(args: argparse.Namespace) -> int:
    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    doc = json.loads(raw)
    parsed = doc.get("parsed") or doc
    db = CharterFactsDB(Path(args.db) if args.db else default_db_path())
    conn = db.connect()
    try:
        db.save_parsed(
            conn,
            message_id=doc.get("message_id") or "",
            email_date_utc=doc.get("email_date_utc") or "",
            from_addr=doc.get("from_addr") or "",
            subject=doc.get("subject") or "",
            parsed=parsed if isinstance(parsed, dict) else {},
        )
    finally:
        conn.close()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    db = CharterFactsDB(Path(args.db) if args.db else default_db_path())
    conn = db.connect()
    try:
        rows = db.search(conn, args.query, limit=args.limit)
    finally:
        conn.close()
    print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_enrich(args: argparse.Namespace) -> int:
    stats = enrich_database(Path(args.db) if args.db else default_db_path())
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0 if stats.get("ok") else 1


def cmd_query_by_port(args: argparse.Namespace) -> int:
    rows = query_by_port(
        Path(args.db) if args.db else default_db_path(),
        args.port,
        limit=args.limit,
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="hifleet-mytonnages charter_facts SQLite 工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("save", help="从 JSON 写入（默认读标准输入，或用 -f 指定文件）")
    ps.add_argument("--db", help="sqlite3 路径（默认 ~/.openclaw/.../charter_facts.sqlite3）")
    ps.add_argument("--file", "-f", help="JSON 文件路径（未指定则从 stdin 读取）")
    ps.set_defaults(func=cmd_save)

    pr = sub.add_parser("search", help="关键词检索 search_text")
    pr.add_argument("--db", help="sqlite3 路径（默认 ~/.openclaw/.../charter_facts.sqlite3）")
    pr.add_argument("query")
    pr.add_argument("--limit", type=int, default=50)
    pr.set_defaults(func=cmd_search)

    pe = sub.add_parser("enrich", help="调用 ttseapi 补充船舶档案与 portid 并写回 SQLite")
    pe.add_argument("--db", help="sqlite3 路径")
    pe.set_defaults(func=cmd_enrich)

    pq = sub.add_parser("query-by-port", help="按查询港口距离升序返回船盘/货盘")
    pq.add_argument("--db", help="sqlite3 路径")
    pq.add_argument("--port", required=True, help="查询港口名（英文或邮件中的写法）")
    pq.add_argument("--limit", type=int, default=50)
    pq.set_defaults(func=cmd_query_by_port)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
