#!/usr/bin/env python3
"""Remotive — a free, public remote-jobs API (good for any remote role).

No key required. Searches by your keywords; returns worldwide-remote postings.
The pipeline then applies your exclude terms and (optionally) location terms.
Great out-of-the-box source for anyone open to remote work.
"""

import json

from .base import Source, http_get
from ..models import job


class Remotive(Source):
    name = "remotive"

    def fetch(self, cfg, log):
        keywords = cfg.get("search", {}).get("keywords", []) or [""]
        out, seen = [], set()
        for kw in keywords:
            try:
                d = json.loads(http_get("https://remotive.com/api/remote-jobs?search=%s"
                                        % kw.replace(" ", "+")))
            except Exception as e:
                log("remotive '%s': %s" % (kw, e))
                continue
            for j in d.get("jobs", []):
                jid = "remotive:%s" % j.get("id")
                if jid in seen:
                    continue
                seen.add(jid)
                out.append(job(jid, j.get("title", ""), j.get("company_name", ""),
                               j.get("candidate_required_location", "Remote"), j.get("url", ""),
                               (j.get("publication_date", "") or "")[:10], "remotive",
                               description=j.get("description", "")))
        log("remotive: fetched %d posting(s)" % len(out))
        return out
