#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取船舶最新位置信息。
需配置环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN。
用法: python get_position.py <MMSI>
"""
import os
import sys
import urllib.request
import urllib.parse
import json

API_URL = "https://api.hifleet.com/position/position/get/token"


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_position(mmsi: str, usertoken: str) -> dict:
    params = {"mmsi": mmsi, "usertoken": usertoken}
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    token = get_token()
    if not token:
        print("请先配置 HiFleet 授权 token（环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN）", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2:
        print("用法: python get_position.py <MMSI>", file=sys.stderr)
        sys.exit(1)
    mmsi = sys.argv[1].strip()
    if not mmsi.isdigit() or len(mmsi) != 9:
        print("MMSI 应为 9 位数字", file=sys.stderr)
        sys.exit(1)
    try:
        data = get_position(mmsi, token)
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    if data.get("result") != "ok":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(1)
    lst = data.get("list", {})
    lat_deg = float(lst.get("la", 0) or 0) / 60
    lon_deg = float(lst.get("lo", 0) or 0) / 60
    out = {
        "mmsi": lst.get("m"),
        "name": lst.get("n"),
        "time": lst.get("ti"),
        "lat_deg": round(lat_deg, 6),
        "lon_deg": round(lon_deg, 6),
        "speed_kn": lst.get("sp"),
        "course_deg": lst.get("co"),
        "destination": lst.get("destination"),
        "status": lst.get("status"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
