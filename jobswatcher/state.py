#!/usr/bin/env python3
"""Persistent "seen" store so a job is sent only once.

A small JSON file maps job id -> first-seen timestamp. Old entries are pruned so
the file never grows without bound. Also holds per-source throttle timestamps."""

import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEEN_FILE = ROOT / "data" / "seen.json"
STATE_FILE = ROOT / "data" / "state.json"
_PRUNE_DAYS = 90


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


class Seen:
    def __init__(self):
        self._data = _load(SEEN_FILE, {})

    def has(self, job_id):
        return job_id in self._data

    def add(self, job_id):
        self._data[job_id] = time.time()

    def save(self):
        cutoff = time.time() - _PRUNE_DAYS * 86400
        self._data = {k: v for k, v in self._data.items() if v >= cutoff}
        _save(SEEN_FILE, self._data)


def due(key, interval_minutes):
    """True if `interval_minutes` have passed since this key last ran."""
    if interval_minutes <= 0:
        return True
    st = _load(STATE_FILE, {})
    return (time.time() - st.get(key, 0)) / 60.0 >= interval_minutes


def mark(key):
    st = _load(STATE_FILE, {})
    st[key] = time.time()
    _save(STATE_FILE, st)
