#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取船舶最新位置信息。支持关键字（船名或 MMSI）或直接 MMSI 查询。
两步流程：先 position/shipSearch 搜船，再 position/position/get/token 查位。
需配置环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN。

用法:
  python get_position.py <MMSI>              # 直接查位（9 位 MMSI）
  python get_position.py <船名或关键字>        # 先搜船：1 条则直接查位，多条则列出并提示指定 MMSI
  python get_position.py <关键字> <MMSI>     # 多条命中时，用第二个参数指定要查的 MMSI
"""
import os
import sys
import urllib.request
import urllib.parse
import json

SHIP_SEARCH_URL = "https://api.hifleet.com/position/shipSearch"
POSITION_GET_URL = "https://api.hifleet.com/position/position/get/token"


def get_token():
    return os.environ.get("HIFLEET_USER_TOKEN") or os.environ.get("HIFLEET_USERTOKEN")


def ship_search(shipname: str, usertoken: str, i18n: str = "zh", count: str = "50") -> dict:
    """按船名或 MMSI 关键字搜索船舶。"""
    params = {
        "shipname": shipname,
        "usertoken": usertoken,
        "i18n": i18n,
        "count": count,
    }
    url = SHIP_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_position(mmsi: str, usertoken: str) -> dict:
    """根据 MMSI 获取最新船位。"""
    params = {"mmsi": mmsi, "usertoken": usertoken}
    url = POSITION_GET_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def print_position(data: dict) -> None:
    """解析位置 API 的 list 并打印可读结果。"""
    lst = data.get("list", {})
    if not lst:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
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


def main():
    token = get_token()
    if not token:
        print("请先配置 HiFleet 授权 token（环境变量 HIFLEET_USER_TOKEN 或 HIFLEET_USERTOKEN）", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2:
        print("用法: python get_position.py <MMSI> 或 python get_position.py <船名或关键字> [MMSI]", file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1].strip()
    chosen_mmsi = sys.argv[2].strip() if len(sys.argv) > 2 else None

    # 已是 9 位数字 MMSI：直接查位
    if keyword.isdigit() and len(keyword) == 9:
        mmsi = chosen_mmsi if chosen_mmsi and chosen_mmsi.isdigit() and len(chosen_mmsi) == 9 else keyword
        try:
            data = get_position(mmsi, token)
        except Exception as e:
            print(f"请求失败: {e}", file=sys.stderr)
            sys.exit(1)
        if data.get("result") != "ok":
            print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
            sys.exit(1)
        print_position(data)
        return

    # 关键字模式：先搜船
    try:
        search_data = ship_search(keyword, token)
    except Exception as e:
        print(f"船舶搜索失败: {e}", file=sys.stderr)
        sys.exit(1)
    if search_data.get("result") != "ok":
        print(json.dumps(search_data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    num = search_data.get("num", 0)
    lst = search_data.get("list", [])

    if num == 0:
        print("未找到匹配船舶，请检查关键字。", file=sys.stderr)
        sys.exit(1)

    if num == 1:
        mmsi = lst[0].get("mmsi")
        if not mmsi:
            print("搜索结果无 MMSI", file=sys.stderr)
            sys.exit(1)
    else:
        # 用户已通过第二参数指定 MMSI
        if chosen_mmsi and chosen_mmsi.isdigit() and len(chosen_mmsi) == 9:
            if not any(s.get("mmsi") == chosen_mmsi for s in lst):
                print(f"指定的 MMSI {chosen_mmsi} 不在搜索结果中。", file=sys.stderr)
                sys.exit(1)
            mmsi = chosen_mmsi
        else:
            # 尝试推断：关键字是否为某条记录的完整 MMSI 或唯一船名
            keyword_upper = keyword.upper()
            by_mmsi = [s for s in lst if s.get("mmsi") == keyword]
            by_name = [s for s in lst if (s.get("name") or "").upper() == keyword_upper]
            if by_mmsi:
                mmsi = by_mmsi[0].get("mmsi")
            elif len(by_name) == 1:
                mmsi = by_name[0].get("mmsi")
            else:
                # 无法唯一确定，列出列表并提示用户指定 MMSI
                print("命中多条船舶，请指定 MMSI 后重试：", file=sys.stderr)
                for s in lst:
                    print(
                        f"  {s.get('name', '')}  MMSI: {s.get('mmsi', '')}  类型: {s.get('type', '')}  船籍: {s.get('dn', '')}",
                        file=sys.stderr,
                    )
                print("用法: python get_position.py <关键字> <MMSI>", file=sys.stderr)
                sys.exit(1)

    try:
        data = get_position(mmsi, token)
    except Exception as e:
        print(f"位置查询失败: {e}", file=sys.stderr)
        sys.exit(1)
    if data.get("result") != "ok":
        print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
    print_position(data)


if __name__ == "__main__":
    main()
