#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source .venv/bin/activate >/dev/null 2>&1 || true
source conformance/assert.sh

reset_replay_db
conformance/bin/build_fixtures.sh
# Keep CRL inactive for baseline tests; X05 enables it explicitly.
rm -f conformance/vectors/crl.active.json

# Start gateway demo
GATEWAY_LOG="conformance/state/gateway.log"
python -m uvicorn demo.gateway_server:app --host 127.0.0.1 --port 8089 >"$GATEWAY_LOG" 2>&1 &
GATEWAY_PID=$!
cleanup() {
  kill "$GATEWAY_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Wait for server to become healthy
python - <<'PY'
import time
import urllib.request

for _ in range(60):
  try:
    urllib.request.urlopen("http://127.0.0.1:8089/metrics", timeout=0.5)
    print("gateway up")
    break
  except Exception:
    time.sleep(0.1)
else:
  raise SystemExit("gateway failed to start")
PY

# Reset gateway state + replay db
python - <<'PY'
import urllib.request
req = urllib.request.Request(
  "http://127.0.0.1:8089/reset",
  data=b"{}",
  headers={"Content-Type": "application/json"},
  method="POST",
)
urllib.request.urlopen(req, timeout=2).read()
PY

# Report skeleton
python - <<'PY'
import json
import time
r = {"version": "0.1", "started_at": time.time(), "results": []}
json.dump(r, open("conformance/report.json", "w"), indent=2)
PY

record() {
  local id="$1"; shift
  local status="$1"; shift
  local note="${1:-}"
  python - <<PY
import json
import time
p = "conformance/report.json"
r = json.load(open(p))
r["results"].append({"id": "$id", "status": "$status", "note": "$note", "ts": time.time()})
json.dump(r, open(p, "w"), indent=2)
PY
}

expect_fail_code() {
  local testid="$1"; shift
  local file="$1"; shift
  local code="$1"; shift
  # forward remaining args to verifier
  expect_stdout_contains "$testid" "$code" python tools/verify_receipt.py "$file" "$@"
}

gateway_expect() {
  local testid="$1"; shift
  local path="$1"; shift
  local body_json="$1"; shift
  local expected_status="$1"; shift
  local expected_substr="$1"; shift
  local receipt_path="${1:-}"

  if ! python - "$path" "$body_json" "$expected_status" "$expected_substr" "$receipt_path" <<'PY'
import json
import sys
import urllib.request
from urllib.error import HTTPError

path, body_json, expected_status, expected_substr, receipt_path = sys.argv[1:6]
expected_status = int(expected_status)

headers = {"Content-Type": "application/json"}
if receipt_path:
  headers["X-SVS-Receipt"] = json.dumps(json.load(open(receipt_path, "r", encoding="utf-8")), ensure_ascii=False)

req = urllib.request.Request(
  f"http://127.0.0.1:8089{path}",
  data=body_json.encode("utf-8"),
  headers=headers,
  method="POST",
)

status = None
body = ""
try:
  resp = urllib.request.urlopen(req, timeout=3)
  status = resp.status
  body = resp.read().decode("utf-8")
except HTTPError as e:
  status = e.code
  body = e.read().decode("utf-8")

if status != expected_status:
  print(f"unexpected status: got={status} expected={expected_status}")
  print(body)
  raise SystemExit(1)

if expected_substr not in body:
  print(f"missing substring: {expected_substr}")
  print(body)
  raise SystemExit(1)
PY
  then
    fail "$testid"
  fi
  pass "$testid"
}

gateway_reset() {
  python - <<'PY'
import urllib.request
req = urllib.request.Request(
  "http://127.0.0.1:8089/reset",
  data=b"{}",
  headers={"Content-Type": "application/json"},
  method="POST",
)
urllib.request.urlopen(req, timeout=2).read()
PY
}

# T01 No receipt, no action (gateway)
gateway_expect "T01" "/execute" '{"action":"do","mode":"commit","payload":{}}' 403 "SVS_GATE_MISSING_RECEIPT"
record "T01" "PASS" "gateway enforces missing receipt"

# T02 Signature verification required (valid receipt passes)
reset_replay_db
expect_stdout_contains "T02" "PASS" python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
record "T02" "PASS" "valid signed receipt verified"

# T03 Forged receipt rejected (receipt signature invalid)
reset_replay_db
expect_fail_code "T03" conformance/vectors/forge_receipt_sig.json "FAIL: SVS_SIG_INVALID_SIGNATURE"
record "T03" "PASS" "invalid receipt signature rejected"

# T04 Tamper detection (modify effect/tool)
reset_replay_db
expect_fail_code "T04a" conformance/vectors/tamper_effect.json "FAIL: SVS_SIG_INVALID_SIGNATURE"
record "T04a" "PASS" "tamper effect rejected"

reset_replay_db
expect_fail_code "T04b" conformance/vectors/tamper_tool.json "FAIL: SVS_SIG_INVALID_SIGNATURE"
record "T04b" "PASS" "tamper tool rejected"

# T05 Replay protection (verify same receipt twice)
reset_replay_db
expect_stdout_contains "T05a" "PASS" python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
expect_fail_code "T05b" examples/signed/allow.receipt.signed.json "FAIL: SVS_REPLAY_DETECTED"
record "T05" "PASS" "replay detected"

# T06 Time window enforcement (expired receipt)
reset_replay_db
expect_fail_code "T06" conformance/vectors/expire_receipt.json "FAIL: SVS_TIME_EXPIRED_RECEIPT"
record "T06" "PASS" "time window enforced"

# T07 Bypass path blocked (gateway)
gateway_expect "T07" "/bypass" '{"action":"do","mode":"commit","payload":{}}' 403 "SVS_GATE_MISSING_RECEIPT"
record "T07" "PASS" "bypass requires receipt"

# T08 DENY receipts mandatory -> verify deny receipts can be signed & verified
reset_replay_db
expect_stdout_contains "T08" "PASS" python tools/verify_receipt.py examples/signed/deny.receipt.signed.json
record "T08" "PASS" "deny receipt verified"

# T09 DEGRADE constraints enforced (gateway)
gateway_reset
gateway_expect "T09a" "/execute" '{"action":"do","mode":"commit","payload":{}}' 403 "SVS_DEGRADE_PREVIEW_ONLY" "examples/signed/degrade.receipt.signed.json"
gateway_reset
gateway_expect "T09b" "/execute" '{"action":"do","mode":"preview","payload":{}}' 200 "DEGRADED_PREVIEW" "examples/signed/degrade.receipt.signed.json"
record "T09" "PASS" "degrade preview-only enforced"

# T10 Completeness accounting (gateway)
gateway_reset
gateway_expect "T10a" "/execute" '{"action":"do","mode":"commit","payload":{}}' 200 "ALLOWED" "examples/signed/allow.receipt.signed.json"
if ! python - <<'PY'
import json
import urllib.request
m = json.loads(urllib.request.urlopen("http://127.0.0.1:8089/metrics", timeout=2).read().decode("utf-8"))
pr = m.get("protected_requests", 0)
rv = m.get("receipts_verified", 0)
if pr != rv:
  raise SystemExit(f"FAIL pr={pr} rv={rv}")
print("PASS")
PY
then
  fail "T10"
fi
pass "T10"
record "T10" "PASS" "metrics reconciled"

# Extra cert chain failures
reset_replay_db
expect_fail_code "X01" conformance/vectors/remove_cert.json "FAIL: SVS_CERT_MISSING_CERT"
record "X01" "PASS" "missing cert rejected"

reset_replay_db
expect_fail_code "X02" conformance/vectors/wrong_issuer.json "FAIL: SVS_CERT_WRONG_ISSUER"
record "X02" "PASS" "wrong issuer rejected"

reset_replay_db
expect_fail_code "X03" conformance/vectors/forge_cert_sig.json "FAIL: SVS_CERT_INVALID_SIGNATURE"
record "X03" "PASS" "forged cert signature rejected"


reset_replay_db
expect_fail_code "X04" conformance/vectors/unknown_reason.signed.json "FAIL: SVS_POLICY_VIOLATION"
record "X04" "PASS" "unknown reason_code rejected by schema enum"


# X05 Revoked certificate must fail
reset_replay_db
bash conformance/bin/build_crl.sh
expect_fail_code "X05" examples/signed/allow.receipt.signed.json "FAIL: SVS_CERT_REVOKED" --crl conformance/vectors/crl.active.json
record "X05" "PASS" "revoked cert rejected"

# X06 Tampered CRL must fail verification (trust failure, not revocation)
reset_replay_db
expect_fail_code "X06" examples/signed/allow.receipt.signed.json "FAIL: SVS_CERT_INVALID_SIGNATURE" --crl conformance/vectors/crl.tampered.json
record "X06" "PASS" "tampered CRL rejected"

python - <<'PY'
import json
import time
p = "conformance/report.json"
r = json.load(open(p))
r["finished_at"] = time.time()
statuses = [x["status"] for x in r["results"]]
r["overall"] = "PASS" if all(s == "PASS" for s in statuses) else "FAIL"
json.dump(r, open(p, "w"), indent=2)
print("Overall:", r["overall"])
print("Report:", p)
PY

# Emit and verify compatibility attestation
python tools/compat_emit.py --report conformance/report.json --out dist/svs-compat.attestation.json
python tools/compat_verify.py dist/svs-compat.attestation.json
