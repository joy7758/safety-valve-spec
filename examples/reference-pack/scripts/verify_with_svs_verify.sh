#!/usr/bin/env bash
set -euo pipefail

ART_DIR="examples/reference-pack/artifacts"
mkdir -p "$ART_DIR"

echo "[svs-verify] install package (editable)"
python -m pip install -U pip >/dev/null
python -m pip install -e packages/svs_verify >/dev/null

echo "[svs-verify] verify attestation"
svs-verify attestation dist/svs-compat.attestation.json --root-pk-file keys/root_ca.pk.b64 | tee "$ART_DIR/svs_verify_attestation.txt"

echo "[svs-verify] done: $ART_DIR/svs_verify_attestation.txt"
