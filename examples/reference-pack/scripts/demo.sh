#!/usr/bin/env bash
set -euo pipefail

ART_DIR="examples/reference-pack/artifacts"
mkdir -p "$ART_DIR"

echo "[1/7] ensure keys"
test -f keys/root_ca.pk.b64 || python tools/ca_generate_root.py
test -f keys/impl.cert.json || python tools/ca_issue_cert.py

echo "[2/7] sign allow receipt"
mkdir -p examples/signed
python tools/receipt_sign.py examples/allow.receipt.json examples/signed/allow.receipt.signed.json

echo "[3/7] build b64 header"
ALLOW_B64="$(python tools/receipt_to_b64.py examples/signed/allow.receipt.signed.json)"

echo "[4/7] wait for gateway"
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

echo "[5/7] call gateway /execute"
curl -s -X POST http://gateway:8089/execute \
  -H "Content-Type: application/json" \
  -H "X-SVS-Receipt-B64: ${ALLOW_B64}" \
  -d '{"action":"demo_action","mode":"commit","payload":{"hello":"world"}}' \
  | tee "$ART_DIR/gateway_response.json"

echo "[6/7] optionally run conformance + emit SVS proofs"
if [ "${DEMO_WITH_CONFORMANCE:-0}" = "1" ]; then
  bash conformance/run.sh | tee "$ART_DIR/conformance.log"

  # Copy runtime artifacts into reference-pack artifacts for user visibility
  test -f conformance/report.json && cp -f conformance/report.json "$ART_DIR/" || true
  test -f dist/svs-compat.attestation.json && cp -f dist/svs-compat.attestation.json "$ART_DIR/" || true
  test -f dist/svs-compat.latest.json && cp -f dist/svs-compat.latest.json "$ART_DIR/" || true
  test -f dist/svs-compat.badge.svg && cp -f dist/svs-compat.badge.svg "$ART_DIR/" || true
  test -f dist/svs-compat.badge.md && cp -f dist/svs-compat.badge.md "$ART_DIR/" || true

  echo "Artifacts copied to: $ART_DIR/"

# Verify attestation using standalone svs-verify
bash examples/reference-pack/scripts/verify_with_svs_verify.sh

else
  echo "Skipped conformance. To include proofs: set DEMO_WITH_CONFORMANCE=1"
fi

echo "[7/7] done."
