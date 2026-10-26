#!/usr/bin/env python3
"""Generic, config-driven relevance filtering.

A job is kept when it is NOT excluded and (optionally) matches at least one of
your keywords. Matching is whole-word, so short terms don't hit inside bigger
words (e.g. "ios" won't match "senior"). Works for any field of work — the user
supplies their own keywords and exclude terms in config.
"""

import re


def _term_match(text, term):
    term = (term or "").strip().lower()
    if not term:
        return False
    return re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(term), text) is not None


def matches(job, search):
    """True if this job passes the search's include/exclude/location rules."""
    title = (job.get("title", "") or "").lower()
    text = (title + " " + (job.get("description", "") or "")).lower()
    loc = (job.get("location", "") or "").lower()

    exclude = search.get("exclude_title_terms", []) or []
    if any(_term_match(title, t) for t in exclude):
        return False

    keywords = search.get("keywords", []) or []
    if search.get("require_title_match", True) and keywords:
        # keyword must appear in the TITLE (tight, low-noise)
        if not any(_term_match(title, k) for k in keywords):
            return False
    elif keywords:
        # looser: keyword anywhere in title or description
        if not any(_term_match(text, k) for k in keywords):
            return False

    loc_terms = search.get("location_terms", []) or []
    if loc_terms:
        if not any(t.lower() in loc for t in loc_terms):
            return False

    return True
