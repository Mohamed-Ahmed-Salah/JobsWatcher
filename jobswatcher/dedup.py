#!/usr/bin/env python3
"""Cross-source near-duplicate collapsing.

The same role often appears on several sources (and across cities). We treat
"same company + same title" as one job and keep a single copy, so you aren't
alerted five times for one opening."""

import re


def _key(job):
    comp = re.sub(r"[^a-z0-9]", "", (job.get("company", "") or "").lower())
    title = re.sub(r"[^a-z0-9]", "", (job.get("title", "") or "").lower())
    return comp, title


def collapse(jobs):
    seen, out = set(), []
    for j in jobs:
        k = _key(j)
        if k in seen:
            continue
        seen.add(k)
        out.append(j)
    return out
