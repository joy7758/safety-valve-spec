#!/usr/bin/env bash
set -euo pipefail

echo "[doctor] docker:"; (docker --version || true)
echo "[doctor] docker compose:"; (docker compose version || true)
echo "[doctor] docker-compose:"; (docker-compose --version || true)

if docker compose version >/dev/null 2>&1; then
  echo "[doctor] OK: use 'docker compose'"
  exit 0
fi

if docker-compose --version >/dev/null 2>&1; then
  echo "[doctor] OK: use 'docker-compose'"
  exit 0
fi

echo "[doctor] FAIL: neither 'docker compose' nor 'docker-compose' found in PATH"
exit 1
