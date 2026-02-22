#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] ensure keys"
test -f keys/root_ca.pk.b64 || python tools/ca_generate_root.py
test -f keys/impl.cert.json || python tools/ca_issue_cert.py

echo "[2/6] sign allow receipt"
mkdir -p examples/signed
python tools/receipt_sign.py examples/allow.receipt.json examples/signed/allow.receipt.signed.json

echo "[3/6] build b64 header"
ALLOW_B64="$(python tools/receipt_to_b64.py examples/signed/allow.receipt.signed.json)"

echo "[4/6] wait for gateway"
python - <<'PY'
import time
import urllib.request
for _ in range(80):
  try:
    urllib.request.urlopen("http://gateway:8089/metrics", timeout=0.5)
    print("gateway up")
    break
  except Exception:
    time.sleep(0.1)
else:
  raise SystemExit("gateway not ready")
PY

echo "[5/6] call gateway /execute"
curl -s -X POST http://gateway:8089/execute \
  -H "Content-Type: application/json" \
  -H "X-SVS-Receipt-B64: ${ALLOW_B64}" \
  -d '{"action":"demo_action","mode":"commit","payload":{"hello":"world"}}' \
  | tee examples/reference-pack/artifacts/gateway_response.json

echo "[6/6] done. response saved: examples/reference-pack/artifacts/gateway_response.json"
