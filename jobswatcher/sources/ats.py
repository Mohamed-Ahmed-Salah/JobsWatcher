#!/usr/bin/env python3
"""Employer-direct ATS boards — public JSON, no keys.

Many companies publish jobs to an Applicant Tracking System whose board has a
public JSON API. Add the company slugs you care about under sources.ats in
config. Returns every posting; the pipeline then filters by your keywords and
locations. Supported: Greenhouse, Lever, Workable, SmartRecruiters, Ashby.
"""

import json
import time
from datetime import datetime, timezone

from .base import Source, http_get
from ..models import job


def _date(ts):
    if not ts:
        return ""
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return str(ts)[:10]


def _greenhouse(slug):
    d = json.loads(http_get("https://boards-api.greenhouse.io/v1/boards/%s/jobs?content=false" % slug))
    name = (d.get("meta") or {}).get("board", {}).get("name") or slug
    return [job("gh:%s:%s" % (slug, j.get("id")), j.get("title", ""), name,
                (j.get("location") or {}).get("name", ""), j.get("absolute_url", ""),
                _date(j.get("updated_at")), "greenhouse") for j in d.get("jobs", [])]


def _lever(slug):
    d = json.loads(http_get("https://api.lever.co/v0/postings/%s?mode=json" % slug))
    return [job("lv:%s:%s" % (slug, j.get("id")), j.get("text", ""),
                slug.replace("-", " ").title(), (j.get("categories") or {}).get("location", ""),
                j.get("hostedUrl", ""), _date(j.get("createdAt")), "lever")
            for j in (d if isinstance(d, list) else [])]


def _workable(slug):
    d = json.loads(http_get("https://www.workable.com/api/accounts/%s" % slug))
    name = d.get("name") or slug
    out = []
    for j in d.get("jobs", []):
        loc = " ".join(x for x in (j.get("city", ""), j.get("state", ""), j.get("country", "")) if x)
        out.append(job("wk:%s:%s" % (slug, j.get("shortcode")), j.get("title", ""), name, loc,
                       j.get("shortlink") or j.get("url", ""),
                       _date(j.get("published_on") or j.get("created_at")), "workable"))
    return out


def _smartrecruiters(slug):
    d = json.loads(http_get("https://api.smartrecruiters.com/v1/companies/%s/postings?limit=100" % slug))
    out = []
    for p in d.get("content", []):
        loc = p.get("location") or {}
        locstr = " ".join(x for x in (loc.get("city", ""), loc.get("region", ""), loc.get("country", "")) if x)
        out.append(job("sr:%s:%s" % (slug, p.get("id")), p.get("name", ""),
                       (p.get("company") or {}).get("name") or slug, locstr,
                       "https://jobs.smartrecruiters.com/%s/%s" % (slug, p.get("id")),
                       _date(p.get("releasedDate")), "smartrecruiters"))
    return out


def _ashby(slug):
    d = json.loads(http_get("https://api.ashbyhq.com/posting-api/job-board/%s?includeCompensation=false" % slug))
    out = []
    for j in d.get("jobs", []):
        if not j.get("isListed", True):
            continue
        out.append(job("ash:%s:%s" % (slug, j.get("id")), (j.get("title", "") or "").strip(),
                       slug.replace("-", " ").title(), j.get("location", ""),
                       j.get("jobUrl") or j.get("applyUrl", ""), _date(j.get("publishedAt")), "ashby"))
    return out


_PLATFORMS = {"greenhouse": _greenhouse, "lever": _lever, "workable": _workable,
              "smartrecruiters": _smartrecruiters, "ashby": _ashby}


class ATS(Source):
    name = "ats"

    def fetch(self, cfg, log):
        conf = cfg.get("sources", {}).get("ats", {})
        delay = cfg.get("options", {}).get("request_delay_seconds", 1)
        out, total = [], 0
        for platform, fn in _PLATFORMS.items():
            for slug in conf.get(platform, []) or []:
                total += 1
                try:
                    out += fn(slug)
                except Exception as e:
                    log("ats %s '%s': %s" % (platform, slug, e))
                time.sleep(min(delay, 1))
        log("ats: fetched %d posting(s) from %d board(s)" % (len(out), total))
        return out
