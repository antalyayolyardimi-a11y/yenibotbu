#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "[i] TELEGRAM_BOT_TOKEN yok. Sadece tarama modu başlatılıyor." >&2
  exec python -m trading_bot.main
else
  echo "[i] Telegram ile orchestrator başlatılıyor..." >&2
  exec python -m trading_bot.orchestrator
fi
