#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source conformance/assert.sh

reset_replay_db
conformance/bin/build_fixtures.sh

# Report skeleton
REPORT="conformance/report.json"
python - <<'PY'
import json, time
r={"version":"0.1","started_at":time.time(),"results":[]}
json.dump(r, open("conformance/report.json","w"), indent=2)
PY

record() {
  local id="$1"; shift
  local status="$1"; shift
  local note="${1:-}"
  python - <<PY
import json, time
p="conformance/report.json"
r=json.load(open(p))
r["results"].append({"id":"$id","status":"$status","note":"$note","ts":time.time()})
json.dump(r, open(p,"w"), indent=2)
PY
}

# Helper to run verifier and check FAIL code substring
expect_fail_code() {
  local testid="$1"; shift
  local file="$1"; shift
  local code="$1"; shift
  expect_stdout_contains "$testid" "$code" python tools/verify_receipt.py "$file"
}

# T01 No receipt, no action -> needs action boundary; SKIP
record "T01" "SKIP" "requires action-boundary demo"

# T02 Signature verification required (valid receipt passes)
reset_replay_db
expect_stdout_contains "T02" "PASS" python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
record "T02" "PASS" "valid signed receipt verified"

# T03 Forged receipt rejected (receipt signature invalid)
reset_replay_db
expect_fail_code "T03" conformance/vectors/forge_receipt_sig.json "FAIL: INVALID_SIGNATURE"
record "T03" "PASS" "invalid receipt signature rejected"

# T04 Tamper detection (modify effect/tool)
reset_replay_db
expect_fail_code "T04a" conformance/vectors/tamper_effect.json "FAIL: INVALID_SIGNATURE"
record "T04a" "PASS" "tamper effect rejected"

reset_replay_db
expect_fail_code "T04b" conformance/vectors/tamper_tool.json "FAIL: INVALID_SIGNATURE"
record "T04b" "PASS" "tamper tool rejected"

# T05 Replay protection (verify same receipt twice)
reset_replay_db
expect_stdout_contains "T05a" "PASS" python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
expect_fail_code "T05b" examples/signed/allow.receipt.signed.json "FAIL: REPLAY_DETECTED"
record "T05" "PASS" "replay detected"

# T06 Time window enforcement (expired receipt)
reset_replay_db
expect_fail_code "T06" conformance/vectors/expire_receipt.json "FAIL: EXPIRED_RECEIPT"
record "T06" "PASS" "time window enforced"

# T07 Bypass path blocked -> needs action boundary; SKIP
record "T07" "SKIP" "requires action-boundary demo"

# T08 DENY receipts mandatory -> we can at least verify deny receipts can be signed & verified
reset_replay_db
expect_stdout_contains "T08" "PASS" python tools/verify_receipt.py examples/signed/deny.receipt.signed.json
record "T08" "PASS" "deny receipt verified"

# T09 DEGRADE constraints enforced -> needs action boundary; SKIP
record "T09" "SKIP" "requires action-boundary demo"

# T10 Completeness accounting -> needs action boundary metrics; SKIP
record "T10" "SKIP" "requires action-boundary demo"

# Extra cert chain failures (not explicitly listed but critical)
reset_replay_db
expect_fail_code "X01" conformance/vectors/remove_cert.json "FAIL: MISSING_CERT"
record "X01" "PASS" "missing cert rejected"

reset_replay_db
expect_fail_code "X02" conformance/vectors/wrong_issuer.json "FAIL: CERT_WRONG_ISSUER"
record "X02" "PASS" "wrong issuer rejected"

reset_replay_db
expect_fail_code "X03" conformance/vectors/forge_cert_sig.json "FAIL: CERT_INVALID_SIGNATURE"
record "X03" "PASS" "forged cert signature rejected"

python - <<'PY'
import json, time
p="conformance/report.json"
r=json.load(open(p))
r["finished_at"]=time.time()
# overall
statuses=[x["status"] for x in r["results"]]
r["overall"]="PASS" if all(s in ("PASS","SKIP") for s in statuses) else "FAIL"
json.dump(r, open(p,"w"), indent=2)
print("Overall:", r["overall"])
print("Report:", p)
PY
