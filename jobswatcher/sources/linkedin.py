#!/usr/bin/env python3
"""LinkedIn public jobs (the guest 'seeMoreJobPostings' endpoint).

Keyword x location search of LinkedIn's PUBLIC job pages — no login, pure
stdlib. Personal use only: automated access is against LinkedIn's Terms of
Service, so keep volume low. Throttled via sources.linkedin.min_interval_minutes
so a frequent scheduler doesn't hammer it from one IP.
"""

import re
import time
import urllib.parse

from .base import Source, http_get
from ..models import job
from .. import state

ENDPOINT = ("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            "?keywords=%s&location=%s&start=0")
_AGE = {1: "r86400", 3: "r259200", 7: "r604800", 14: "r1209600", 30: "r2592000"}


def _parse(html):
    out = []
    for card in re.split(r"<li>", html):
        urn = re.search(r'data-entity-urn="urn:li:jobPosting:(\d+)"', card)
        link = re.search(r'<a[^>]*class="base-card__full-link"[^>]*href="([^"?]+)', card)
        title = re.search(r'class="base-search-card__title">\s*(.*?)\s*</h3>', card, re.S)
        comp = re.search(r'class="base-search-card__subtitle">.*?<a[^>]*>\s*(.*?)\s*</a>', card, re.S)
        loc = re.search(r'class="job-search-card__location">\s*(.*?)\s*</span>', card, re.S)
        date = re.search(r'<time[^>]*datetime="([^"]+)"', card)
        jid = urn.group(1) if urn else (re.search(r"-(\d+)$", link.group(1)) if link else None)
        if isinstance(jid, re.Match):
            jid = jid.group(1)
        if not jid or not title:
            continue
        clean = lambda m: re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        out.append(job(
            id="linkedin:%s" % jid,
            title=clean(title), company=clean(comp), location=clean(loc),
            url=(link.group(1) if link else "https://www.linkedin.com/jobs/view/%s" % jid),
            date=(date.group(1)[:10] if date else ""), source="linkedin",
        ))
    return out


class LinkedIn(Source):
    name = "linkedin"

    def fetch(self, cfg, log):
        conf = cfg.get("sources", {}).get("linkedin", {})
        interval = conf.get("min_interval_minutes", 30)
        if not state.due("linkedin", interval):
            log("linkedin: throttled (min interval %d min)" % interval)
            return []
        search = cfg.get("search", {})
        keywords = search.get("keywords", [])
        locations = search.get("locations", []) or [""]
        age = _AGE.get(search.get("jobage_days", 7), "r604800")
        delay = cfg.get("options", {}).get("request_delay_seconds", 3)
        out, seen = [], set()
        for loc in locations:
            for kw in keywords:
                url = ENDPOINT % (urllib.parse.quote(kw), urllib.parse.quote(loc))
                url += "&f_TPR=" + age
                try:
                    html = http_get(url, accept="text/html")
                except Exception as e:
                    log("linkedin '%s'@'%s': %s" % (kw, loc, e))
                    continue
                for j in _parse(html):
                    if j["id"] not in seen:
                        seen.add(j["id"])
                        out.append(j)
                time.sleep(delay)
        state.mark("linkedin")
        log("linkedin: fetched %d posting(s)" % len(out))
        return out
