#!/usr/bin/env python3
"""Command-line entry point.

  python -m jobswatcher              run once: send new jobs to Telegram
  python -m jobswatcher --dry-run    print new jobs, send/save nothing
  python -m jobswatcher --init       mark current jobs seen, send nothing (first run)
  python -m jobswatcher --whoami     print chat ids that messaged your bot
  python -m jobswatcher --config X   use a specific config file
"""

import argparse
import sys

from . import config as cfgmod
from . import pipeline
from . import telegram as tg


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jobswatcher", description="Send new jobs to Telegram.")
    ap.add_argument("--dry-run", action="store_true", help="print new jobs, don't send/save")
    ap.add_argument("--init", action="store_true", help="mark current jobs seen, send nothing")
    ap.add_argument("--whoami", action="store_true", help="print your Telegram chat id")
    ap.add_argument("--config", help="path to a config file")
    args = ap.parse_args(argv)

    cfg = cfgmod.load(args.config)

    if args.whoami:
        token = cfgmod.get(cfg, "telegram.bot_token", "")
        if not token:
            print("Set telegram.bot_token in config.json first.")
            return 1
        tg.whoami(token)
        return 0

    pipeline.run(cfg, dry_run=args.dry_run, init=args.init)
    return 0


if __name__ == "__main__":
    sys.exit(main())
