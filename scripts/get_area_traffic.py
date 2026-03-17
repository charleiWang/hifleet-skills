#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询指定区域内的当前船舶。支持 bbox（左下经度,左下纬度,右上经度,右上纬度）。
需配置环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN。

用法:
  python get_area_traffic.py <左下经度> <左下纬度> <右上经度> <右上纬度>
  例如: python get_area_traffic.py 120 15 121 17

Security: 仅向 https://api.hifleet.com/position/gettraffic/token 发起 GET 请求；token 仅用于 API 鉴权；仅使用标准库，无 eval/exec。
"""
import os
import sys
import urllib.request
import urllib.parse
import json

AREA_TRAFFIC_URL = "https://api.hifleet.com/position/gettraffic/token"


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_area_traffic(bbox: str, usertoken: str) -> dict:
    """bbox: 左下经度,左下纬度,右上经度,右上纬度"""
    params = {"bbox": bbox, "usertoken": usertoken}
    url = AREA_TRAFFIC_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    token = get_token()
    if not token:
        print("请先配置 HiFleet 授权 token（环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN）", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 5:
        print("用法: python get_area_traffic.py <左下经度> <左下纬度> <右上经度> <右上纬度>", file=sys.stderr)
        print("例如: python get_area_traffic.py 120 15 121 17", file=sys.stderr)
        sys.exit(1)
    try:
        lon_min = float(sys.argv[1])
        lat_min = float(sys.argv[2])
        lon_max = float(sys.argv[3])
        lat_max = float(sys.argv[4])
    except ValueError:
        print("经纬度须为数字", file=sys.stderr)
        sys.exit(1)
    if lon_min >= lon_max or lat_min >= lat_max:
        print("请保证 左下经度 < 右上经度 且 左下纬度 < 右上纬度", file=sys.stderr)
        sys.exit(1)
    bbox = "%s,%s,%s,%s" % (lon_min, lat_min, lon_max, lat_max)
    try:
        data = get_area_traffic(bbox, token)
    except Exception as e:
        print("请求失败: %s" % e, file=sys.stderr)
        sys.exit(1)
    if data.get("result") != "ok":
        print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
