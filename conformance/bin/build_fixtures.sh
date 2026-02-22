#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate >/dev/null 2>&1 || true
python -m pip install cryptography >/dev/null 2>&1 || true

mkdir -p examples/signed conformance/vectors conformance/state

# Ensure keys exist
test -f keys/root_ca.pk.b64 || python tools/ca_generate_root.py
test -f keys/impl.cert.json || python tools/ca_issue_cert.py

# Refresh issued_at so receipts are inside verifier time window.
python - <<'PY'
import datetime
import json
from pathlib import Path

now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
for name in ("allow", "deny", "degrade"):
  src = Path(f"examples/{name}.receipt.json")
  dst = Path(f"conformance/state/{name}.receipt.fresh.json")
  r = json.loads(src.read_text(encoding="utf-8"))
  r["issued_at"] = now
  dst.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

# Sign fresh receipts.
python tools/receipt_sign.py conformance/state/allow.receipt.fresh.json examples/signed/allow.receipt.signed.json
python tools/receipt_sign.py conformance/state/deny.receipt.fresh.json examples/signed/deny.receipt.signed.json
python tools/receipt_sign.py conformance/state/degrade.receipt.fresh.json examples/signed/degrade.receipt.signed.json
rm -f conformance/state/allow.receipt.fresh.json conformance/state/deny.receipt.fresh.json conformance/state/degrade.receipt.fresh.json

# Build negative vectors from allow signed
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/tamper_effect.json tamper_effect
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/tamper_tool.json tamper_tool
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/remove_cert.json remove_cert
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/wrong_issuer.json wrong_issuer
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/expire_receipt.json expire_receipt
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/forge_receipt_sig.json forge_receipt_sig
python conformance/bin/mutate_receipt.py examples/signed/allow.receipt.signed.json conformance/vectors/forge_cert_sig.json forge_cert_sig
