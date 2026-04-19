# Scheduling — Daily Ghost→Supabase Sync

This document explains how the nightly safety-net sync is scheduled, and why it
uses **launchd** rather than a GitHub Actions workflow.

## What runs

- `scripts/ghost_backfill_posts.py` — reads all published posts from the Ghost
  Admin API via CDP and idempotently upserts them into Supabase
  `content_posts`. Runs every night at **21:00 JST**.

## Why launchd, not GitHub Actions

`ghost_auto_publish.py` and `ghost_backfill_posts.py` both connect to the Ghost
Admin session by attaching to a **locally running Chrome via CDP**
(`http://127.0.0.1:18800`). This dependency is intentional — it lets the
scripts reuse Eason's authenticated browser session without storing the Admin
API key anywhere.

GitHub Actions runners have no such browser, and no way to reach
`127.0.0.1:18800` on Eason's machine. Two alternatives were considered and
rejected:

1. **Self-hosted GitHub runner on Eason's Mac** — adds an always-on agent just
   to trigger one nightly job. Not worth the complexity.
2. **Refactor scripts to use Ghost Admin API key directly** — viable but out of
   scope for this PR, and requires a new secret management decision.

`launchd` is macOS's native per-user cron replacement. It fires on the user's
wall clock (honors `TZ=Asia/Tokyo`), runs only while the user is logged in, and
has clean stdout/stderr redirection.

## Installation

```bash
# 1. Copy the plist into user LaunchAgents
cp deploy/com.eason.ghost-auto-publish.plist \
   ~/Library/LaunchAgents/com.eason.ghost-auto-publish.plist

# 2. Load it
launchctl load ~/Library/LaunchAgents/com.eason.ghost-auto-publish.plist

# 3. Verify it's scheduled
launchctl list | grep ghost-auto-publish
```

## Verifying it runs

- Structured log: `logs/scheduler.log` — one line per phase
  (`run.start` / `cdp.ok` / `backfill.ok` / `run.end`).
- launchd stdout/stderr: `logs/scheduler.stdout.log`,
  `logs/scheduler.stderr.log`.
- Manual smoke test:

  ```bash
  bash deploy/daily_ghost_publish.sh
  tail -n 20 logs/scheduler.log
  ```

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.eason.ghost-auto-publish.plist
rm ~/Library/LaunchAgents/com.eason.ghost-auto-publish.plist
```

## Behavior when Chrome/CDP is unavailable

If `http://127.0.0.1:18800/json/version` doesn't respond within 3 seconds, the
wrapper logs `run.skip reason=cdp_unreachable` and exits 0. This is intentional
— a failed scheduled run shouldn't retry-storm launchd. The skip is visible in
`logs/scheduler.log` for the next review.
