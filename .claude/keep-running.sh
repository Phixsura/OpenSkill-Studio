#!/usr/bin/env bash
# keep-running.sh — 无限持续运行守护脚本
set -uo pipefail
CHECK_INTERVAL=30

log() { echo "[$(date '+%H:%M:%S')] $*"; }

bring_iterm_front() {
  osascript -e 'tell application "iTerm" to activate' 2>/dev/null || true
}

check_loom() {
  if ! pgrep -xq "Loom"; then
    log "⚠️  Loom not running — launching..."
    open -a "Loom" 2>/dev/null || true
    sleep 3
  fi
}

log "🚀 Guardian started — runs until manually stopped"

while true; do
  bring_iterm_front
  check_loom
  sleep $CHECK_INTERVAL
done
