# JobsWatcher — tiny, dependency-free image. Self-schedules via --loop.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="JobsWatcher" \
      org.opencontainers.image.description="Configurable job watcher that sends new jobs to Telegram" \
      org.opencontainers.image.source="https://github.com/Mohamed-Ahmed-Salah/JobsWatcher" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY jobswatcher ./jobswatcher
COPY config.example.json README.md LICENSE ./

# How often (minutes) the loop runs. Override with -e RUN_EVERY_MIN=30
ENV RUN_EVERY_MIN=15 \
    PYTHONUNBUFFERED=1

# Runs forever: scans every RUN_EVERY_MIN minutes, sending only new jobs.
ENTRYPOINT ["sh", "-c", "exec python -m jobswatcher --loop ${RUN_EVERY_MIN}"]
