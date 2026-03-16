#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 IMO 号获取船舶档案（基本信息、尺度、舱容、建造、入级、动力、公司信息、互保协会等）。
需配置环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN。

用法: python get_archive.py <IMO>
IMO 一般为 7 位数字（如 1000112）。若只有船名或 MMSI，可先用 get_position 或 shipSearch 查到 IMO 再调用本脚本。
"""
import os
import sys
import urllib.request
import urllib.parse
import json

ARCHIVE_URL = "https://api.hifleet.com/shiparchive/getShipArchiveWithEnginAndCompany"


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_archive(imo: str, usertoken: str) -> dict:
    """根据 IMO 获取船舶档案。"""
    params = {"imo": imo.strip(), "usertoken": usertoken}
    url = ARCHIVE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _format_value(item: dict, indent: str) -> list:
    """递归格式化一条 value 项，返回要打印的行列表。"""
    lines = []
    val = item.get("value")
    label_zh = (item.get("labelZh") or "").strip()
    # 嵌套结构：value 是列表
    if isinstance(val, list) and len(val) > 0:
        if label_zh:
            lines.append(indent + label_zh + ":")
        next_indent = indent + "  "
        for sub in val:
            if isinstance(sub, dict):
                lines.extend(_format_value(sub, next_indent))
    else:
        # 键值行：用 valueZh，无则用 value
        disp = item.get("valueZh")
        if disp is None:
            disp = item.get("value")
        if disp is None:
            disp = ""
        if isinstance(disp, str) and disp.strip() == "" and not label_zh:
            return lines
        if label_zh:
            lines.append(indent + label_zh + ": " + str(disp))
    return lines


def print_archive(data: dict) -> None:
    """按 data 分块打印档案，使用 labelZh / valueZh。"""
    blocks = data.get("data") or []
    if not blocks:
        if data.get("status") != "1":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    for block in blocks:
        title = block.get("labelZh") or block.get("key") or ""
        vals = block.get("value")
        if not title and not vals:
            continue
        print("\n【" + title + "】")
        if isinstance(vals, list):
            for item in vals:
                if isinstance(item, dict):
                    for line in _format_value(item, "  "):
                        print(line)
    print()


def main():
    token = get_token()
    if not token:
        print("请先配置 HiFleet 授权 token（环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN）", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2:
        print("用法: python get_archive.py <IMO>", file=sys.stderr)
        sys.exit(1)
    imo_raw = sys.argv[1].strip()
    # 支持纯数字或 IMO 前缀
    imo = imo_raw.upper().replace("IMO", "").strip() if imo_raw.upper().startswith("IMO") else imo_raw
    if not imo.isdigit() or len(imo) < 6:
        print("IMO 应为数字（通常 7 位）", file=sys.stderr)
        sys.exit(1)
    try:
        raw = get_archive(imo, token)
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    if raw.get("status") != "1":
        print(json.dumps(raw, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
    print_archive(raw)


if __name__ == "__main__":
    main()
