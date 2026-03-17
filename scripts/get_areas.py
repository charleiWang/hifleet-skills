#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取区域清单（海区、贸易区），供用户按名称选择区域后使用 areaId 查询区域船舶。
可选配置环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN（传 usertoken 时 includeBound 才生效）。

用法:
  python get_areas.py [--include-bound]
  无参数时仅返回区域列表；--include-bound 时返回边界 WKT（需 usertoken 有效）。

Security: 仅向 https://api.hifleet.com/position/areas/token 发起 GET 请求；仅使用标准库，无 eval/exec。
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

AREAS_URL = "https://api.hifleet.com/position/areas/token"


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def get_areas(usertoken: str = None, include_bound: bool = False) -> dict:
    params = {}
    if usertoken:
        params["usertoken"] = usertoken
    if include_bound:
        params["includeBound"] = "true"
    url = AREAS_URL + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="获取区域清单（海区、贸易区）")
    parser.add_argument(
        "--include-bound",
        action="store_true",
        help="是否返回边界 WKT（仅 usertoken 有效时生效）",
    )
    args = parser.parse_args()

    token = get_token() if args.include_bound else None
    if args.include_bound and not token:
        print("使用 --include-bound 时请配置 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN", file=sys.stderr)
        sys.exit(1)

    try:
        data = get_areas(usertoken=token, include_bound=args.include_bound)
    except Exception as e:
        print("请求失败: %s" % e, file=sys.stderr)
        sys.exit(1)

    if data.get("result") != "ok":
        print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
