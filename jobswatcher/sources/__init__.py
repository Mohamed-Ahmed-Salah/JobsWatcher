#!/usr/bin/env python3
"""Source registry.

ALL_SOURCES lists every connector. collect() runs the enabled ones in parallel
and returns all jobs. Adding a source = create a module here and append it below.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from .linkedin import LinkedIn
from .ats import ATS
from .remotive import Remotive

ALL_SOURCES = [LinkedIn(), ATS(), Remotive()]


def collect(cfg, log):
    enabled = [s for s in ALL_SOURCES if s.enabled(cfg)]
    jobs = []
    if not enabled:
        return jobs

    def _run(src):
        try:
            return src.fetch(cfg, log) or []
        except Exception as e:
            log("%s source error: %s" % (src.name, e))
            return []

    with ThreadPoolExecutor(max_workers=len(enabled)) as ex:
        for fut in as_completed([ex.submit(_run, s) for s in enabled]):
            jobs.extend(fut.result())
    return jobs
