#!/usr/bin/env bash
# daily_ghost_publish.sh — Runs nightly Ghost→Supabase sync.
#
# Triggered by:
#   deploy/com.eason.ghost-auto-publish.plist  (launchd, 21:00 JST)
#
# Behavior:
#   1. Verify Chrome CDP is reachable (required by ghost_backfill_posts.py).
#   2. If reachable → run ghost_backfill_posts.py to sync any posts published
#      manually that day into Supabase content_posts (idempotent upsert).
#   3. Append structured log line to logs/scheduler.log.
#   4. Exit 0 even on CDP unreachable (don't spam launchd with retries;
#      absence is captured in the log for later review).
#
# Why backfill, not ghost_auto_publish.py:
#   ghost_auto_publish.py publishes a *specific HTML file*. There's no single
#   file to publish nightly — content creation is manual. What *can* be
#   automated is the Supabase sync safety-net, which closes the gap that
#   caused issue #3 (9-day silent drift from 2026-04-10).

set -u

REPO_DIR="/Users/dljapan/.openclaw/workspace-ghost"
LOG_DIR="${REPO_DIR}/logs"
LOG_FILE="${LOG_DIR}/scheduler.log"
PYTHON="/opt/homebrew/bin/python3.13"
CDP_PORT="18800"

mkdir -p "${LOG_DIR}"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "$(ts) [scheduler] $*" >> "${LOG_FILE}"; }

log "run.start tz=Asia/Tokyo local=$(TZ=Asia/Tokyo date +%H:%M)"

if ! curl -sf -o /dev/null --max-time 3 "http://127.0.0.1:${CDP_PORT}/json/version"; then
  log "run.skip reason=cdp_unreachable port=${CDP_PORT}"
  log "run.end status=skipped"
  exit 0
fi

log "cdp.ok port=${CDP_PORT}"

cd "${REPO_DIR}" || { log "run.fail reason=cd_failed"; exit 0; }

start=$(date +%s)
if "${PYTHON}" scripts/ghost_backfill_posts.py >> "${LOG_FILE}" 2>&1; then
  dur=$(( $(date +%s) - start ))
  log "backfill.ok duration_s=${dur}"
  log "run.end status=ok"
else
  rc=$?
  dur=$(( $(date +%s) - start ))
  log "backfill.fail rc=${rc} duration_s=${dur}"
  log "run.end status=failed"
fi

exit 0
