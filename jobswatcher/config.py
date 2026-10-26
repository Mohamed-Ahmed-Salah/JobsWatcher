#!/usr/bin/env python3
"""Configuration loading.

All behaviour is driven by a single JSON file (default: config.json, falling
back to config.example.json). Secrets may also come from environment variables,
which win over the file — handy for servers and CI:

  TELEGRAM_BOT_TOKEN   overrides telegram.bot_token
  TELEGRAM_CHAT_ID     overrides telegram.chat_id
"""

import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load(path=None):
    """Load config.json (or the given path), else config.example.json."""
    candidates = [path] if path else []
    candidates += [ROOT / "config.json", ROOT / "config.example.json"]
    for p in candidates:
        if p and pathlib.Path(p).exists():
            with open(p) as f:
                cfg = json.load(f)
            return _with_env(cfg)
    raise FileNotFoundError("No config.json or config.example.json found.")


def _with_env(cfg):
    tg = cfg.setdefault("telegram", {})
    tg["bot_token"] = (os.environ.get("TELEGRAM_BOT_TOKEN") or tg.get("bot_token", "")).strip()
    tg["chat_id"] = (os.environ.get("TELEGRAM_CHAT_ID") or str(tg.get("chat_id", ""))).strip()
    return cfg


# tiny dotted-path getter: get(cfg, "sources.linkedin.enabled", False)
def get(cfg, dotted, default=None):
    cur = cfg
    for key in dotted.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur
