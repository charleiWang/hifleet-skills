#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原始邮件预览 HTTP 服务（供前端「查看原邮件」按钮跳转）。

启动:
  python scripts/mail_preview_server.py
  python scripts/mail_preview_server.py --host 0.0.0.0 --port 8765

前端:
  GET /api/mail/preview-url?message_id=<urlencoded>
  或直接使用 search / query-by-port 返回的 preview_url 字段
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from imap_mail import (  # noqa: E402
    build_preview_url,
    fetch_raw_by_preview_token,
    fetch_raw_email,
    get_attachment_part,
    load_preview_config,
    parse_for_preview,
    preview_token_for_message_id,
)

logger = logging.getLogger("mail_preview_server")

_PREVIEW_CFG = load_preview_config()
_PREVIEW_SECRET = _PREVIEW_CFG.get("mail_preview_token") or ""


def _cors_origin() -> str:
    return "*"  # 前端与预览服务常不同端口；生产可改为配置白名单


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", _cors_origin())
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, status: int, content: str) -> None:
    body = content.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", _cors_origin())
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _bytes_response(
    handler: BaseHTTPRequestHandler,
    status: int,
    data: bytes,
    content_type: str,
    filename: str = "",
) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Access-Control-Allow-Origin", _cors_origin())
    if filename:
        safe = re.sub(r'[^\w\-. ]', "_", filename)[:200]
        handler.send_header("Content-Disposition", f'inline; filename="{safe}"')
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _check_auth(handler: BaseHTTPRequestHandler) -> bool:
    if not _PREVIEW_SECRET:
        return True
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
    qtok = (qs.get("auth") or qs.get("token") or [""])[0]
    header = handler.headers.get("X-HIFLEET-Preview-Token", "")
    return qtok == _PREVIEW_SECRET or header == _PREVIEW_SECRET


def _render_preview_page(token: str, parsed: dict[str, Any], meta: dict[str, Any]) -> str:
    subject = html.escape(parsed.get("subject") or meta.get("subject") or "(无主题)")
    from_addr = html.escape(parsed.get("from_addr") or meta.get("from_addr") or "")
    to_addr = html.escape(parsed.get("to_addr") or "")
    date = html.escape(parsed.get("date") or meta.get("email_date_utc") or "")
    message_id = html.escape(str(meta.get("message_id") or ""))

    att_rows = ""
    for att in parsed.get("attachments") or []:
        name = html.escape(str(att.get("filename") or "attachment"))
        size = int(att.get("size") or 0)
        url = html.escape(str(att.get("url") or ""))
        att_rows += f'<li><a href="{url}" target="_blank" rel="noopener">{name}</a> ({size} bytes)</li>'

    attachments_html = ""
    if att_rows:
        attachments_html = f"<h3>附件</h3><ul>{att_rows}</ul>"

    html_body = parsed.get("html_body") or ""
    text_body = html.escape(parsed.get("text_body") or "")
    if html_body:
        body_block = (
            f'<div class="mail-html"><iframe sandbox="" srcdoc="{html.escape(html_body, quote=True)}"></iframe></div>'
        )
    elif text_body:
        body_block = f'<pre class="mail-text">{text_body}</pre>'
    else:
        body_block = '<p class="empty">（无正文）</p>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{subject}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f4f6f8; color: #1a1a1a; }}
    .wrap {{ max-width: 960px; margin: 0 auto; padding: 16px; }}
    .card {{ background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 20px; }}
    h1 {{ font-size: 1.25rem; margin: 0 0 12px; }}
    .meta {{ font-size: 0.875rem; color: #555; line-height: 1.6; margin-bottom: 16px; }}
    .meta dt {{ font-weight: 600; display: inline; }}
    .meta dd {{ display: inline; margin: 0 16px 0 4px; }}
    .mail-html iframe {{ width: 100%; min-height: 480px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; }}
    pre.mail-text {{ white-space: pre-wrap; word-break: break-word; background: #fafafa; padding: 12px; border-radius: 4px; border: 1px solid #eee; }}
    ul {{ padding-left: 1.2rem; }}
    .badge {{ display: inline-block; background: #e8f0fe; color: #1967d2; font-size: 12px; padding: 2px 8px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <p><span class="badge">原始邮件</span></p>
      <h1>{subject}</h1>
      <dl class="meta">
        <dt>发件人</dt><dd>{from_addr}</dd>
        <dt>收件人</dt><dd>{to_addr or "—"}</dd>
        <dt>时间</dt><dd>{date}</dd>
      </dl>
      {attachments_html}
      <h3>正文</h3>
      {body_block}
      <p class="meta" style="margin-top:24px"><small>Message-ID: {message_id}</small></p>
    </div>
  </div>
</body>
</html>"""


class MailPreviewHandler(BaseHTTPRequestHandler):
    server_version = "HiFleetMailPreview/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), fmt % args)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-HIFLEET-Preview-Token, Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if not _check_auth(self):
            _json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return

        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path.rstrip("/") or "/"
        qs = urllib.parse.parse_qs(parsed_path.query)

        try:
            if path == "/health":
                _json_response(self, 200, {"ok": True, "service": "mail_preview"})
                return

            if path == "/api/mail/preview-url":
                mid = (qs.get("message_id") or [""])[0]
                if not mid:
                    _json_response(self, 400, {"ok": False, "error": "message_id required"})
                    return
                url = build_preview_url(mid)
                _json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "message_id": mid,
                        "preview_token": preview_token_for_message_id(mid),
                        "preview_url": url,
                    },
                )
                return

            m = re.match(r"^/mail/preview/([a-f0-9]{32})$", path)
            if m:
                token = m.group(1)
                raw, meta = fetch_raw_by_preview_token(token)
                parsed = parse_for_preview(raw, token)
                page = _render_preview_page(token, parsed, meta)
                _html_response(self, 200, page)
                return

            m = re.match(r"^/mail/attachment/([a-f0-9]{32})/(\d+)$", path)
            if m:
                token = m.group(1)
                part_index = int(m.group(2))
                raw, _meta = fetch_raw_by_preview_token(token)
                part, filename, ctype = get_attachment_part(raw, part_index)
                data = part.get_payload(decode=True) or b""
                _bytes_response(self, 200, data, ctype, filename)
                return

            m = re.match(r"^/api/mail/raw/([a-f0-9]{32})$", path)
            if m:
                token = m.group(1)
                raw, meta = fetch_raw_by_preview_token(token)
                parsed = parse_for_preview(raw, token)
                _json_response(
                    self,
                    200,
                    {"ok": True, "meta": meta, "preview": parsed},
                )
                return

            if path == "/api/mail/fetch":
                mid = (qs.get("message_id") or [""])[0]
                if not mid:
                    _json_response(self, 400, {"ok": False, "error": "message_id required"})
                    return
                raw, meta = fetch_raw_email(mid)
                token = preview_token_for_message_id(mid)
                parsed = parse_for_preview(raw, token)
                _json_response(self, 200, {"ok": True, "meta": meta, "preview": parsed})
                return

            _json_response(self, 404, {"ok": False, "error": "not found"})
        except FileNotFoundError as e:
            _html_response(
                self,
                404,
                f"<html><body><h1>邮件未找到</h1><p>{html.escape(str(e))}</p></body></html>",
            )
        except ValueError as e:
            _json_response(self, 400, {"ok": False, "error": str(e)})
        except Exception as e:
            logger.exception("request failed: %s", self.path)
            _json_response(self, 500, {"ok": False, "error": str(e)})


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_preview_config()
    p = argparse.ArgumentParser(description="HiFleet 原始邮件预览服务")
    p.add_argument("--host", default=cfg["mail_preview_host"])
    p.add_argument("--port", type=int, default=cfg["mail_preview_port"])
    args = p.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), MailPreviewHandler)
    base = cfg["mail_preview_base_url"]
    logger.info("邮件预览服务: http://%s:%s  (对外 base: %s)", args.host, args.port, base)
    logger.info("示例: %s/mail/preview/<token>  |  API: %s/api/mail/preview-url?message_id=...", base, base)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("已停止")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
