#!/usr/bin/env python3
"""The run pipeline: collect -> filter -> dedup -> de-seen -> deliver.

One tick = one call to run(). Designed to be invoked on a schedule (cron /
systemd timer). It only sends jobs it has never sent before.
"""

import pathlib
import time

from . import config as cfgmod
from . import filters
from . import dedup
from . import telegram as tg
from .sources import collect
from .state import Seen

LOG = pathlib.Path(__file__).resolve().parent.parent / "data" / "jobswatcher.log"


def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run(cfg, dry_run=False, init=False):
    token = cfgmod.get(cfg, "telegram.bot_token", "")
    chat = cfgmod.get(cfg, "telegram.chat_id", "")
    search = cfg.get("search", {})
    options = cfg.get("options", {})

    # 1. collect from every enabled source (in parallel)
    raw = collect(cfg, log)

    # 2. filter to what you asked for, then collapse duplicates
    wanted = [j for j in raw if filters.matches(j, search)]
    if options.get("dedup_similar", True):
        wanted = dedup.collapse(wanted)

    # 3. keep only jobs we've never seen
    seen = Seen()
    fresh = [j for j in wanted if not seen.has(j["id"])]
    log("collected %d -> %d matched -> %d new" % (len(raw), len(wanted), len(fresh)))

    if dry_run:
        for j in fresh:
            print("\n" + tg.job_message(j))
        return

    # 4. --init: mark everything seen, send nothing (baseline on first run)
    if init:
        for j in wanted:
            seen.add(j["id"])
        seen.save()
        log("--init: marked %d jobs seen, sent nothing." % len(wanted))
        return

    if not token or not chat:
        log("telegram not configured (bot_token / chat_id); nothing sent.")
        return

    # 5. deliver (cap per run; seed the overflow so it won't re-queue)
    cap = options.get("max_send_per_run", 60)
    to_send = fresh[:cap] if cap else fresh
    for j in fresh[cap:] if cap else []:
        seen.add(j["id"])

    sent = 0
    if to_send:
        try:
            tg.send_text(token, chat, "\U0001F50D <b>%d new job(s)</b>" % len(fresh))
        except Exception as e:
            log("header send failed: %s" % e)
    for j in to_send:
        try:
            tg.send_text(token, chat, tg.job_message(j), markup=tg.job_markup(j))
            seen.add(j["id"])   # mark only after successful send
            sent += 1
            time.sleep(1)
        except Exception as e:
            log("send failed %s: %s" % (j["id"], e))

    # 6. optional "you're up to date" note when nothing new
    if sent == 0 and not fresh and options.get("idle_notice_minutes", 0) > 0:
        from . import state
        if state.due("idle_notice", options["idle_notice_minutes"]):
            try:
                tg.send_text(token, chat, "✅ You're up to date — no new jobs right now.")
            except Exception:
                pass
            state.mark("idle_notice")

    seen.save()
    log("sent %d/%d new job(s)." % (sent, len(fresh)))
