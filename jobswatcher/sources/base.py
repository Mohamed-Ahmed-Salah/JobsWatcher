#!/usr/bin/env python3
"""Source plugin interface.

A source fetches raw postings and returns normalized Job dicts. To add a new
source, drop a module here that subclasses Source and register it in
sources/__init__.py. Keep network calls inside fetch(); never raise — return []
on error so one bad source can't stop the run.
"""

import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def http_get(url, accept="application/json", timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


class Source:
    name = "base"

    def enabled(self, cfg):
        return bool((cfg.get("sources", {}).get(self.name, {}) or {}).get("enabled"))

    def fetch(self, cfg, log):
        return []
