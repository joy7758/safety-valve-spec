#!/usr/bin/env bash
set -euo pipefail

pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; exit 1; }

expect_exit() {
  local name="$1"; shift
  local code="$1"; shift
  set +e
  "$@" >/dev/null 2>&1
  local rc=$?
  set -e
  if [ "$rc" -ne "$code" ]; then
    echo "Expected exit=$code but got rc=$rc for: $*"
    fail "$name"
  fi
  pass "$name"
}

expect_stdout_contains() {
  local name="$1"; shift
  local needle="$1"; shift
  set +e
  out="$("$@" 2>&1)"
  rc=$?
  set -e
  echo "$out" | grep -q "$needle" || { echo "$out"; fail "$name"; }
  pass "$name"
}

reset_replay_db() {
  rm -f conformance/state/seen_nonces.json
}
