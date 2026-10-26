# Deploy JobsWatcher 24/7 (systemd)

Run it on any always-on Linux box (a $5 VPS is plenty).

```bash
# 1. Clone + configure
git clone <your-repo-url> ~/JobsWatcher && cd ~/JobsWatcher
cp config.example.json config.json
nano config.json                      # telegram token + chat_id + your keywords

# 2. Seed current jobs so the first real run doesn't flood you
python3 -m jobswatcher --init

# 3. Install the timer (edit User/WorkingDirectory in the unit files first)
sudo cp deploy/jobswatcher.service /etc/systemd/system/
sudo cp deploy/jobswatcher.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now jobswatcher.timer

# 4. Verify
systemctl list-timers | grep jobswatcher
journalctl -u jobswatcher -n 30 --no-pager
tail -f data/jobswatcher.log
```

## Secrets via environment (optional)
Instead of putting the token in config.json, set:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
(e.g. in an `EnvironmentFile=` for the service). Environment wins over the file.

## cron alternative
```cron
*/15 * * * * cd /home/jobswatcher/JobsWatcher && /usr/bin/python3 -m jobswatcher >> data/cron.log 2>&1
```
