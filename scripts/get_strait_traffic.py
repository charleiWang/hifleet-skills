#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红海与波斯湾海峡船舶通航情况查询。支持曼德海峡、苏伊士运河、好望角、霍尔木兹海峡。
无 usertoken 仅可查最近 1 周；有 usertoken 时间区间不限。接口定义见 ShowDoc: http://showdoc.hifleet.com/web/#/45/2234

用法:
  python get_strait_traffic.py <海峡名或oid> [开始日期] [结束日期]
  海峡: 曼德海峡|苏伊士运河|好望角|霍尔木兹海峡 或 oid(24480|132808|1062830|24471)
  日期: yyyy-MM-dd，不传则默认最近 7 天。无 token 时区间不得超过 7 天。

Security: 仅向 HiFleet 海峡通航接口发起 GET 请求；usertoken 可选，仅用于扩展时间范围；仅使用标准库，无 eval/exec。
"""
import os
import sys
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

# 接口 URL 以 ShowDoc 为准，当前为占位；若文档不同请修改
STRAIT_TRAFFIC_URL = "https://api.hifleet.com/traffic/strait"

STRAITS = {
    "曼德海峡": "24480",
    "苏伊士运河": "132808",
    "好望角": "1062830",
    "霍尔木兹海峡": "24471",
    "24480": "24480",
    "132808": "132808",
    "1062830": "1062830",
    "24471": "24471",
}


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_strait_traffic(oid: str, start_date: str, end_date: str, usertoken: str = None) -> dict:
    """请求海峡通航接口。参数名以 ShowDoc 为准，此处为常见命名。"""
    params = {"oid": oid, "startTime": start_date, "endTime": end_date}
    if usertoken:
        params["usertoken"] = usertoken
    url = STRAIT_TRAFFIC_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    if len(sys.argv) < 2:
        print("用法: python get_strait_traffic.py <海峡名或oid> [开始日期] [结束日期]", file=sys.stderr)
        print("海峡: 曼德海峡 苏伊士运河 好望角 霍尔木兹海峡 或 oid 24480 132808 1062830 24471", file=sys.stderr)
        print("日期: yyyy-MM-dd，不传默认最近 7 天。无 token 时仅支持最近 1 周。", file=sys.stderr)
        sys.exit(1)

    key = sys.argv[1].strip()
    oid = STRAITS.get(key) or (key if key.isdigit() else None)
    if not oid:
        print("未知海峡，支持: 曼德海峡、苏伊士运河、好望角、霍尔木兹海峡 或 oid 24480 132808 1062830 24471", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    today = datetime.now().date()
    if len(sys.argv) >= 4:
        start_s = sys.argv[2].strip()
        end_s = sys.argv[3].strip()
        try:
            start_d = datetime.strptime(start_s, "%Y-%m-%d").date()
            end_d = datetime.strptime(end_s, "%Y-%m-%d").date()
        except ValueError:
            print("日期格式须为 yyyy-MM-dd", file=sys.stderr)
            sys.exit(1)
    else:
        end_d = today
        start_d = today - timedelta(days=6)

    if start_d > end_d:
        print("开始日期不得大于结束日期", file=sys.stderr)
        sys.exit(1)

    delta = (end_d - start_d).days
    if delta > 6:
        delta_days = delta + 1
        if not token:
            print("无 usertoken 时仅可查询最近 1 周（7 天），当前区间为 %d 天。请配置 HIFLEET_USER_TOKEN 或缩短区间。" % delta_days, file=sys.stderr)
            sys.exit(1)

    start_str = start_d.strftime("%Y-%m-%d")
    end_str = end_d.strftime("%Y-%m-%d")

    try:
        data = get_strait_traffic(oid, start_str, end_str, token)
    except Exception as e:
        print("请求失败: %s" % e, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
