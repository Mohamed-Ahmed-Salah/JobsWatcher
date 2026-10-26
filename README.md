# JobsWatcher

**A lightweight, configurable job watcher that pushes new job postings straight to your Telegram.**

Set your keywords and locations once, pick your sources, and JobsWatcher scans on a schedule and sends you **only new** matching jobs — one clean message per job, deduplicated, with a direct link. No account, no database, no paid API required to get started.

It's **field-agnostic**: a mobile developer, a cybersecurity engineer, a designer or an accountant all use the *same* tool — just different keywords in the config.

```
🆕 Flutter Developer
🏢 Acme Technologies
📍 Riyadh, Saudi Arabia  ·  🗓️ 2026-02-10
📡 Linkedin
🔗 https://www.linkedin.com/jobs/view/…
            [ 🔗 Open job ]
```

---

## Features

- 🔌 **Multiple sources** — LinkedIn (public), Remotive (free remote-jobs API), and employer ATS boards (Greenhouse, Lever, Workable, SmartRecruiters, Ashby)
- 🧩 **Plugin architecture** — add a source in one file; sources fetch **in parallel**
- 🎯 **Dynamic config** — everything (keywords, exclude terms, locations, sources, interval) lives in one JSON file
- 🔁 **No duplicates** — a persistent "seen" store means each job is sent once; cross-source de-duplication collapses the same role seen in several places
- 📣 **Telegram delivery** — one message per job with an *Open job* button
- 🪶 **Zero dependencies** — pure Python standard library (3.9+). Runs anywhere.

---

## Quick start

```bash
# 1. Get the code
git clone <your-repo-url> JobsWatcher && cd JobsWatcher

# 2. Create your config
cp config.example.json config.json

# 3. Create a Telegram bot: message @BotFather -> /newbot -> copy the token
#    Then message YOUR new bot once, and find your chat id:
python -m jobswatcher --whoami        # after putting the token in config.json

# 4. Fill config.json: telegram token + chat_id, and your keywords/locations

# 5. First run — seed current jobs as "seen" so you don't get flooded:
python -m jobswatcher --init

# 6. From now on, run it on a schedule to receive ONLY new jobs:
python -m jobswatcher
```

Preview without sending anything:

```bash
python -m jobswatcher --dry-run
```

---

## Configuration (`config.json`)

| Key | Meaning |
|-----|---------|
| `telegram.bot_token` | Token from @BotFather (or env `TELEGRAM_BOT_TOKEN`) |
| `telegram.chat_id` | Your chat id from `--whoami` (or env `TELEGRAM_CHAT_ID`) |
| `search.keywords` | Job titles/roles you want (e.g. `["flutter developer"]`) |
| `search.exclude_title_terms` | Titles to drop (e.g. `["senior","intern"]`) |
| `search.locations` | Locations to search on LinkedIn (`"Remote"` works) |
| `search.location_terms` | *Optional* post-filter: keep a job only if its location text contains one of these (e.g. `["riyadh","dubai","remote"]`). Leave `[]` to keep all. |
| `search.jobage_days` | How recent (LinkedIn): `1,3,7,14,30` |
| `search.require_title_match` | `true` = keyword must be in the **title** (tight); `false` = anywhere |
| `sources.linkedin.enabled` | Turn LinkedIn on/off |
| `sources.linkedin.min_interval_minutes` | Throttle LinkedIn (protects your IP) |
| `sources.remotive.enabled` | Turn the free remote-jobs source on/off |
| `sources.ats.*` | Lists of company slugs per ATS platform |
| `options.max_send_per_run` | Cap messages per run (overflow is seeded, not lost) |
| `options.dedup_similar` | Collapse the same role across sources/cities |
| `options.idle_notice_minutes` | `>0` sends a periodic "you're up to date" ping |
| `options.request_delay_seconds` | Politeness delay between requests |

### Tip: choosing keywords
Real job titles vary, so prefer **short, title-friendly terms** over long phrases.
`"flutter"` matches *Flutter Engineer*, *Senior Flutter Developer*, *Mobile Dev (Flutter)*;
`"flutter developer"` would match none of those. Add a few variants and let
`exclude_title_terms` trim what you don't want.

### Adding ATS companies
Find a company's slug from its careers URL, e.g. `boards.greenhouse.io/**acme**` → add `"acme"` under `sources.ats.greenhouse`, and set `sources.ats.enabled: true`.

---

## Running on a schedule

**cron** (every 15 minutes):
```cron
*/15 * * * * cd /path/to/JobsWatcher && /usr/bin/python3 -m jobswatcher >> data/cron.log 2>&1
```

**systemd** (24/7 on a server): see [`deploy/DEPLOY.md`](deploy/DEPLOY.md).

---

## Project structure

```
jobswatcher/
├── __main__.py        # CLI entry (run / --dry-run / --init / --whoami)
├── config.py          # config + env loading
├── models.py          # the Job schema
├── pipeline.py        # collect → filter → dedup → de-seen → deliver
├── filters.py         # keyword / exclude / location matching
├── dedup.py           # cross-source de-duplication
├── state.py           # persistent "seen" store + throttles
├── telegram.py        # Telegram delivery
└── sources/           # one file per source (plugin)
    ├── base.py        linkedin.py  ats.py  remotive.py
```

---

## Notes & limits

- **LinkedIn** reads public job pages; automated access is against LinkedIn's Terms of Service, so keep volume modest (the built-in throttle helps). Personal use only.
- Runtime state lives in `data/` (git-ignored): `seen.json`, `state.json`, logs.
- Want Indeed/Glassdoor or Gulf boards (Bayt, GulfTalent)? Those need a paid scraping API — add them as new source plugins.

## License

MIT — see [LICENSE](LICENSE).
