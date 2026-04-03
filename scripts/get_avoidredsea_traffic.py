#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集装箱饶航船舶每日统计。、支持查询下饶航红海的集装箱船舶。
对于饶航饶航的方向：东是向东，西是向西。
接口：POST http://112.126.23.236:8234//routerisk//getAvoidRedSeaDetail/token，参数 starttime、endtime、usertoken（可选）。
无 usertoken 仅可查最近 1 周；有 usertoken 时间区间不限。

用法:
  python get_avoidredsea_traffic.py  [开始日期] [结束日期] [i18n]

  日期: yyyy-MM-dd，不传则默认最近 1 天。无 token 时区间不得超过 7 天；有 token 不限。i18n 可选 zh 或 en。

Security: 仅向 http://112.126.23.236:8234//routerisk//getAvoidRedSeaDetail/token 发起 POST 请求；usertoken 可选，仅用于扩展时间范围；仅使用标准库，无 eval/exec。
"""
import os
import sys
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

STRAIT_TRAFFIC_URL = "http://112.126.23.236:8234//routerisk//getAvoidRedSeaDetail/token"




def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_strait_traffic(starttime: str, endtime: str, i18n: str = "zh", usertoken: str = None) -> dict:
    """POST 请求咽喉航道通航统计。有 usertoken 时传入可查任意时间区间。"""
    params = {"starttime": starttime, "endtime": endtime, "i18n": i18n}
    if usertoken:
        params["usertoken"] = usertoken
    url = STRAIT_TRAFFIC_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="POST", data=b"")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():



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
        start_d = today - timedelta(days=1)

    if start_d > end_d:
        print("开始日期不得大于结束日期", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    delta = (end_d - start_d).days
    if delta > 6 and not token:
        print("无 usertoken 时仅可查询最近 1 天（1 天），当前区间为 %d 天。请配置 HIFLEET_USER_TOKEN 或缩短区间。" % (delta + 1), file=sys.stderr)
        sys.exit(1)

    i18n = (sys.argv[4].strip() if len(sys.argv) > 4 else "zh").lower()
    if i18n not in ("zh", "en"):
        i18n = "zh"

    start_str = start_d.strftime("%Y-%m-%d")
    end_str = end_d.strftime("%Y-%m-%d")

    try:
        data = get_strait_traffic(start_str, end_str, i18n, token)
    except Exception as e:
        print("请求失败: %s" % e, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
