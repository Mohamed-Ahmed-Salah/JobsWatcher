#!/usr/bin/env python3
"""Telegram delivery — sends each job as its own message with an Open button."""

import json
import urllib.parse
import urllib.request

API = "https://api.telegram.org/bot%s/%s"


def _call(token, method, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API % (token, method), data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_text(token, chat_id, text, markup=None):
    params = {"chat_id": chat_id, "text": text,
              "parse_mode": "HTML", "disable_web_page_preview": "true"}
    if markup is not None:
        params["reply_markup"] = json.dumps(markup)
    return _call(token, "sendMessage", params)


def job_message(job):
    bits = ["\U0001F195 <b>%s</b>" % _esc(job.get("title", "(no title)"))]
    if job.get("company"):
        bits.append("\U0001F3E2 %s" % _esc(job["company"]))
    line = []
    if job.get("location"):
        line.append("\U0001F4CD %s" % _esc(job["location"]))
    if job.get("date"):
        line.append("\U0001F5D3️ %s" % _esc(job["date"]))
    if line:
        bits.append("  ·  ".join(line))
    if job.get("source"):
        bits.append("\U0001F4E1 %s" % _esc(job["source"].title()))
    return "\n".join(bits)


def job_markup(job):
    if job.get("url"):
        return {"inline_keyboard": [[{"text": "\U0001F517 Open job", "url": job["url"]}]]}
    return None


def whoami(token):
    """Print chat ids that have messaged your bot (run once to find your chat_id)."""
    res = _call(token, "getUpdates", {})
    chats = {}
    for upd in res.get("result", []):
        chat = (upd.get("message") or upd.get("channel_post") or {}).get("chat") or {}
        if chat.get("id") is not None:
            chats[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name") or ""
    if not chats:
        print("No chats found. Send your bot a message in Telegram first, then rerun.")
    for cid, name in chats.items():
        print("chat_id = %s   (%s)" % (cid, name))
