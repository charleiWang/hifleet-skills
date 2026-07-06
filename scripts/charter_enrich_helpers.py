#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Map list/API vessel rows → enrich-row request (parse_schema + top-level imo/mmsi)."""

from __future__ import annotations

import re
from typing import Any, Optional, Tuple


def _norm_imo(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    digits = re.sub(r"\D", "", str(value).strip())
    if len(digits) == 7 and digits != "0000000":
        return digits
    return None


def clean_vessel_name(shipname: str) -> str:
    """Strip MV/MT/M.V. prefix before IMO lookup or enrich (matches charter_enrich_mappers)."""
    if not shipname:
        return ""
    return re.sub(
        r"^(M\s*[\./\\]?\s*(V|T)\s*[\./\\]?\s*)",
        "",
        str(shipname).strip(),
        flags=re.IGNORECASE,
    ).strip()


def normalize_vessel_row_for_enrich(row: dict[str, Any]) -> Tuple[dict[str, Any], Optional[str], Optional[str]]:
    """
    Accept parse_schema (船名/IMO) or public API row (ShipName/imo/dwt).
    Returns (row for body.row, imo for body.imo, mmsi for body.mmsi).
    """
    r = row or {}
    imo = _norm_imo(r.get("IMO") or r.get("imo") or r.get("Imo"))
    mmsi_raw = r.get("mmsi") or r.get("MMSI")
    mmsi = str(mmsi_raw).strip() if mmsi_raw not in (None, "") else None

    out = dict(r)
    if not str(out.get("船名") or "").strip():
        out["船名"] = (
            str(
                r.get("ShipName")
                or r.get("shipName")
                or r.get("vesselName")
                or r.get("name")
                or ""
            ).strip()
        )
    if out.get("载重吨") in (None, "") and r.get("dwt") not in (None, ""):
        out["载重吨"] = r.get("dwt")
    if not out.get("IMO") and imo:
        out["IMO"] = imo
    if not str(out.get("OPEN位置") or "").strip():
        out["OPEN位置"] = (
            str(r.get("OPEN位置") or r.get("openPort") or r.get("destination") or "").strip()
        )
    if not str(out.get("船型") or "").strip():
        out["船型"] = str(r.get("船型") or r.get("type") or r.get("shiptype") or "").strip()
    name = str(out.get("船名") or "").strip()
    if name:
        out["船名"] = clean_vessel_name(name)
    return out, imo, mmsi


def normalize_cargo_row_for_enrich(row: dict[str, Any]) -> dict[str, Any]:
    r = row or {}
    out = dict(r)
    if not str(out.get("货物种类") or "").strip():
        out["货物种类"] = str(
            r.get("货物种类") or r.get("cargoType") or r.get("type") or r.get("cargo") or ""
        ).strip()
    if not str(out.get("装货港") or "").strip():
        out["装货港"] = str(r.get("装货港") or r.get("loadPort") or r.get("openPort") or "").strip()
    if not str(out.get("卸货港") or "").strip():
        out["卸货港"] = str(
            r.get("卸货港") or r.get("dischargePort") or r.get("dischargingPort") or ""
        ).strip()
    if out.get("货物数量") in (None, "") and r.get("quantity") not in (None, ""):
        out["货物数量"] = r.get("quantity")
    return out


def enrich_response_usable(resp: dict[str, Any]) -> bool:
    if not isinstance(resp, dict):
        return False
    if resp.get("ok") is True:
        return True
    if resp.get("imo") or resp.get("data") or resp.get("archive"):
        return True
    code = resp.get("code")
    if code not in (None, 0, 200, "200", "0"):
        return False
    return bool(resp.get("status") in (1, "1", True, "ok", "OK"))
